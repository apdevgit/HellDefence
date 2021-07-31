from flask import Flask, Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from game import Game
from tic_tac_toe import TicTacToeGame
from chess import Chess
from game_concepts import GameType
from play_manager import PlayManager
from http_status import HttpStatus
from flask_jwt_extended import (JWTManager, jwt_required, jwt_optional, create_access_token, get_jwt_identity, get_jwt_claims, decode_token)
from pm_zookeeper_client import ZooKeeperPMClient
import requests


service_blueprint = Blueprint('playmaster', __name__)
service = Api(service_blueprint)

jwt = JWTManager()
plm = PlayManager()

GAMEMASTER_SERVICE_URL = None

def update_gamemaster_url_cb(url):
    global GAMEMASTER_SERVICE_URL
    GAMEMASTER_SERVICE_URL = url

def update_play_manager_callback(play_manager_state, games_json):
    games = {}
    for gj in games_json.values():
        if gj.get('gametype') == 'tic-tac-toe':
            games[gj.get('play_id')] = TicTacToeGame(None, None, None, None, None, None, None)
            games[gj.get('play_id')].LoadStateFromJson(gj)
        elif gj.get('gametype') == 'chess':
            games[gj.get('play_id')] = Chess(None, None, None, None, None, None, None)
            games[gj.get('play_id')].LoadStateFromJson(gj)
    
    plm.LoadState(play_manager_state, games)
    update_host_ownership_to_gm()

def update_host_ownership_to_gm():
    play_ids = list(plm.registeredGames.keys())
    try:
        res = requests.post(GAMEMASTER_SERVICE_URL + 'plays/host', json={'play_ids': play_ids})
    except Exception as e:
        print(str(e)+'20')


zkc = ZooKeeperPMClient(update_gamemaster_url_cb, update_play_manager_callback)

def game_over_action(play_id):
    game = plm.GetGameFromId(play_id)

    winner_id = game.GetTheWinner()
    isADraw = game.IsADraw()

    dictToSend = {'play_id':play_id, 'winner_id':winner_id, 'isADraw':isADraw}
    plm.RemovePlayersOfGame(play_id)
    plm.RemoveGame(play_id)
    zkc.UpdatePlayManager(plm.GetState())
    try:
        res = requests.post(GAMEMASTER_SERVICE_URL + 'plays/result', json=dictToSend)
        zkc.RemoveGame(play_id)
    except requests.exceptions.RequestException as e:
        print(str(e)+'21')

    if res.status_code == HttpStatus.created_201.value:
        pass
    else:
        print('Bad answer from GameMaster when trying to send play result: \n {}'.format(res.text))


def NotifyUIForGameStateChange(play_id, gamestate, access_token_header, isNew = False):
    send_data = gamestate
    send_data['play_id'] = play_id
    send_data['isNew'] = isNew
    send_data = dict(send_data)
    recepients = plm.GetGameUIsRecipients(play_id)
    for ui_url in recepients: 
        try:
            requests.post(ui_url + "games/update", json=send_data, headers=access_token_header)
        except Exception as e:
            print(str(e)+'22')
        



###########################
### Interaction with UI ###
###########################

#| Check GameMaster IP?
class TicTacToeGameRegisterResource(Resource):
    @jwt_required
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input given.'}, HttpStatus.bad_request_400.value

        play_id = args.get('play_id')
        player1_id = args.get('player1_id')
        player2_id = args.get('player2_id')
        player1_username = args.get('player1_username')
        player2_username = args.get('player2_username')
        player1_ui_url = args.get('player1_ui_url')
        player2_ui_url = args.get('player2_ui_url')

        if play_id == None:
            return {'message': 'play_id not given.'}, HttpStatus.bad_request_400.value
        if player1_id == None:
            return {'message': 'player1_id not given.'}, HttpStatus.bad_request_400.value
        if player2_id == None:
            return {'message': 'player2_id not given.'}, HttpStatus.bad_request_400.value

        play_id = int(play_id)
        player1_id = int(player1_id)
        player2_id = int(player2_id)

        if plm.PlayExists(play_id):
            response = {'message': 'Game with id {} already exists'.format(play_id)}
            return response, HttpStatus.bad_request_400.value
        if plm.PlayerIsInPlayingAGame(player1_id):
            response = {'message': 'Player with id {} is playing another game at the moment.'.format(player1_id)}
            return response, HttpStatus.bad_request_400.value
        if plm.PlayerIsInPlayingAGame(player2_id):
            response = {'message': 'Player with id {} is playing another game at the moment.'.format(player2_id)}
            return response, HttpStatus.bad_request_400.value

        game = TicTacToeGame(play_id, player1_id, player2_id, player1_username, player2_username, args.get('tournament_id'), args.get('phase'))
        plm.RegisterGame(play_id, player1_ui_url, player2_ui_url, game)
        zkc.CreateGame(game.play_id, game.GetStateJson())
        zkc.UpdatePlayManager(plm.GetState())
        NotifyUIForGameStateChange(play_id, game.GetState(), {'Authorization': dict(request.headers)['Authorization']}, True)
        response = {'url': '/playmaster/games/tic-tac-toe/{0}'.format(play_id)}                                                 # TODO: FIX IT
        return response, HttpStatus.created_201.value


class TicTacToeGameResource(Resource):
    def get(self, play_id):
        game = plm.GetGameFromId(play_id)
        if game == None or game.GetType() != GameType.TIC_TAC_TOE:
            response = {'message': 'Tic-tac-toe game with id {} doesn\'t exist'.format(play_id)}
            return response, HttpStatus.bad_request_400.value

        game_state = {'game_state': game.squares}

        return game_state, HttpStatus.ok_200.value


class TicTacToeGamePlayMoveResource(Resource):
    @jwt_required
    def post(self, play_id):
        args = request.get_json()
        if not args:
            return {'message': 'No input given.'}, HttpStatus.bad_request_400.value
        
        player_id = get_jwt_identity()
        square_to_play = args.get('square_to_play')
        if square_to_play == None:
            print('square_to_play not given.')
            return {'message': 'square_to_play not given.'}, HttpStatus.bad_request_400.value
        
        player_id = int(player_id)
        square_to_play = int(square_to_play)

        game = plm.GetGameFromId(play_id)
        if game == None:
            print('Game with id {} doesn\'t exist'.format(play_id))
            response = {'message': 'Game with id {} doesn\'t exist'.format(play_id)}
            return response, HttpStatus.bad_request_400.value
        elif game.GetType() != GameType.TIC_TAC_TOE:
            print('Not a tic-tac-toe game.')
            return {'message': 'Not a tic-tac-toe game.'}, HttpStatus.bad_request_400.value
        if not game.PlayerExists(player_id):
            print('Player with id {} is not playing in this game.'.format(player_id))
            return {'message': 'Player with id {} is not playing in this game.'.format(player_id)}, HttpStatus.bad_request_400.value
        if game.WhoPlays() != player_id:
            print('It\'s not your turn.')
            return {'message': 'It\'s not your turn.'}, HttpStatus.bad_request_400.value
        if not game.PlayTurn(square_to_play):
            print('Invalid move (square index: {})'.format(square_to_play))
            response = {'message': 'Invalid move (square index: {})'.format(square_to_play)}
            return response, HttpStatus.bad_request_400.value

        zkc.UpdateGame(play_id, game.GetStateJson())
        NotifyUIForGameStateChange(play_id, game.GetState(), {'Authorization': dict(request.headers)['Authorization']}, True)
        if game.GameIsOver():
            game_over_action(play_id)
        return {}, HttpStatus.ok_200.value

# TODO: Check GameMaster ip?
class ChessGameRegisterResource(Resource):
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input given.'}, HttpStatus.bad_request_400.value

        play_id = args.get('play_id')
        player1_id = args.get('player1_id')
        player2_id = args.get('player2_id')
        player1_username = args.get('player1_username')
        player2_username = args.get('player2_username')
        player1_ui_url = args.get('player1_ui_url')
        player2_ui_url = args.get('player2_ui_url')

        if play_id == None:
            return {'message': 'play_id not given.'}, HttpStatus.bad_request_400.value
        if player1_id == None:
            return {'message': 'player1_id not given.'}, HttpStatus.bad_request_400.value
        if player2_id == None:
            return {'message': 'player2_id not given.'}, HttpStatus.bad_request_400.value

        play_id = int(play_id)
        player1_id = int(player1_id)
        player2_id = int(player2_id)


        if plm.PlayExists(play_id):
            response = {'message': 'Game with id {} already exists'.format(play_id)}
            return response, HttpStatus.bad_request_400.value
        if plm.PlayerIsInPlayingAGame(player1_id):
            response = {'message': 'Player with id {} is playing another game at the moment.'.format(player1_id)}
            return response, HttpStatus.bad_request_400.value
        if plm.PlayerIsInPlayingAGame(player2_id):
            response = {'message': 'Player with id {} is playing another game at the moment.'.format(player2_id)}
            return response, HttpStatus.bad_request_400.value

        game = Chess(play_id, player1_id, player2_id, player1_username, player2_username, args.get('tournament_id'), args.get('phase'))
        plm.RegisterGame(play_id, player1_ui_url, player2_ui_url, game)
        zkc.CreateGame(game.play_id, game.GetStateJson())
        zkc.UpdatePlayManager(plm.GetState())
        NotifyUIForGameStateChange(play_id, game.GetState(), {'Authorization': dict(request.headers)['Authorization']})
        response = {'url': '/playmaster/games/chess/{0}'.format(play_id)}                                                 # TODO: FIX IT
        return response, HttpStatus.created_201.value


class ChessGameResource(Resource):
    def get(self, play_id):
        game = plm.GetGameFromId(play_id)
        if game == None or game.GetType() != GameType.CHESS:
            response = {'message': 'Chess game with id {} doesn\'t exist'.format(play_id)}
            return response, HttpStatus.bad_request_400.value

        game_state = {'game_state': game.GetBoardToString()}                                                                                                    

        return game_state, HttpStatus.ok_200.value


class ChessGamePlayMoveResource(Resource):
    @jwt_required
    def post(self, play_id):
        args = request.get_json()
        if not args:
            return {'message': 'No input given.'}, HttpStatus.bad_request_400.value
        
        player_id = get_jwt_identity()
        square_from = args.get('square_from')
        square_to = args.get('square_to')

        if not square_from:
            return {'message': 'square_to_from not given.'}, HttpStatus.bad_request_400.value
        if not square_to:
            return {'message': 'square_to not given.'}, HttpStatus.bad_request_400.value

        game = plm.GetGameFromId(play_id)
        if game == None:
            response = {'message': 'Game with id {} doesn\'t exist'.format(play_id)}
            return response, HttpStatus.bad_request_400.value
        elif game.GetType() != GameType.CHESS:
            return {'message': 'Not a chess game.'}, HttpStatus.bad_request_400.value
        if not game.PlayerExists(player_id):
            return {'message': 'Player with id {} is not playing in this game.'.format(player_id)}, HttpStatus.bad_request_400.value
        if game.WhoPlays() != player_id:
            return {'message': 'It\'s not your turn.'}, HttpStatus.bad_request_400.value
        if not game.PlayMoveOriginalInput(square_from, square_to):
            response = {'message': 'Invalid move {}->{})'.format(square_from, square_to)}
            return response, HttpStatus.bad_request_400.value

        zkc.UpdateGame(play_id, game.GetStateJson())
        NotifyUIForGameStateChange(play_id, game.GetState(), {'Authorization': dict(request.headers)['Authorization']})
        if game.GameIsOver():
            game_over_action(play_id)
        return {}, HttpStatus.ok_200.value


class GameStateResource(Resource):
    @jwt_required
    def get(self, play_id):
        # Register UI Spectate
        ui_url = 'http://{}:{}/'.format(request.environ['REMOTE_ADDR'], 5000)
        plm.AddSpectator(play_id, ui_url)
        zkc.UpdatePlayManager(plm.GetState())
        game = plm.GetGameFromId(play_id)
        if game != None:
            return game.GetState(), HttpStatus.ok_200.value
        else:
            return {'message': 'Play with id {} doesn\'t exist.'.format(play_id)}, HttpStatus.not_found_404.value
        

class PlayerGameStateResource(Resource):
    @jwt_required
    def get(self, player_id):
        player_asked = get_jwt_identity()
        ui_url = 'http://{}:{}/'.format(request.environ['REMOTE_ADDR'], 5000)
        # If user has changed UI service
        if plm.GetPlayerUIUrl(player_asked) != ui_url:
            plm.UpdatePlayerUIUrl(player_asked, ui_url)
            zkc.UpdatePlayManager(plm.GetState())

        game = plm.GetGameFromPlayer(player_id)
        if game != None:
            return game.GetState(), HttpStatus.ok_200.value
        else:
            return {'message': 'player with id {} is not in any game.'.format(player_id)}, HttpStatus.not_found_404.value


class SpectateUnregisterResource(Resource):
    def post(self, play_id):
        ui_url = 'http://{}:{}/'.format(request.environ['REMOTE_ADDR'], 5000)
        plm.RemoveSpectator(play_id, ui_url)
        zkc.UpdatePlayManager(plm.GetState())
        return {}, HttpStatus.ok_200.value


########################
### Resource Linking ###
########################

service.add_resource(TicTacToeGameRegisterResource, '/games/tic-tac-toe/register')
service.add_resource(TicTacToeGameResource, '/games/tic-tac-toe/<int:play_id>')
service.add_resource(TicTacToeGamePlayMoveResource, '/games/tic-tac-toe/<int:play_id>/play')

service.add_resource(ChessGameRegisterResource, '/games/chess/register')
service.add_resource(ChessGameResource, '/games/chess/<int:play_id>')
service.add_resource(ChessGamePlayMoveResource, '/games/chess/<int:play_id>/play')

service.add_resource(GameStateResource, '/games/<int:play_id>')
service.add_resource(PlayerGameStateResource, '/games/player/<int:player_id>')

service.add_resource(SpectateUnregisterResource, '/spectate/unregister/<int:play_id>')    # POST input: ui_url