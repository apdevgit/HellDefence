from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from http_status import HttpStatus
from models import orm, User, UserSchema, Play, PlaySchema, Tournament, TournamentSchema, UserPlay, UserPlaySchema, UserTotalScore, UserTotalScoreSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from game_concepts import TournamentInfo, Play as PlayData, GameType
from gamemanager import GameManager
from flask_jwt_extended import (JWTManager, jwt_required, jwt_optional, get_jwt_identity, get_jwt_claims)
from gm_zookeeper_client import ZooKeeperGMClient
import requests


service_blueprint = Blueprint('gamemaster', __name__)
user_schema = UserSchema()
play_schema = PlaySchema()
tournament_schema = TournamentSchema()
user_play_schema = UserPlaySchema()
user_total_score_schema = UserTotalScoreSchema()
service = Api(service_blueprint)

jwt = JWTManager()

def administer_play_id_cb(gametype):
    try:
        play = Play(GameType.FromEnumToString(gametype))
        play.add(play)
        return play.id
    except SQLAlchemyError as e:
        orm.session.rollback()
        return None


def administer_tournament_id_cb(participants_num, gametype, creator_id):
    try:
        tournament = Tournament(GameType.FromEnumToString(gametype), participants_num, creator_id)
        tournament.add(tournament)
        return tournament.id
    except SQLAlchemyError:
        orm.session.rollback()
        return None


gm = GameManager(administer_play_id_cb, administer_tournament_id_cb)

def update_playmaster_urls_cb(urls):
    gm.SetPlayMasterURLs(urls)

zkc = ZooKeeperGMClient(update_playmaster_urls_cb)


########################
### GameMaster Views ###
########################

class PlayResource(Resource):
    def get(self, id):
        play = Play.query.get_or_404(id)
        dumped_play = play_schema.dump(play)
        return dumped_play

class PlayListResource(Resource):
    def get(self):
        plays = Play.query.all()
        dumped_result = play_schema.dump(plays, many=True)
        return dumped_result

    def post(self):
        play_dict = request.get_json()
        if not play_dict:
            response = {'message': 'No input provided'}
            return response, HttpStatus.bad_request_400.value

        errors = play_schema.validate(play_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value

        try:
            play = Play(play_dict['gametype'])
            play.add(play)
            query = Play.query.get(play.id)
            dumped_result = play_schema.dump(query)
            return dumped_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value

class TournamentResource(Resource):
    def get(self, id):
        tournament = Tournament.query.get_or_404(id)
        dumped_tournament = tournament_schema.dump(tournament)
        return dumped_tournament

class TournamentListResource(Resource):
    def get(self):
        tournaments = Tournament.query.all()
        dumped_result = tournament_schema.dump(tournaments, many=True)
        return dumped_result

    def post(self):
        tournament_dict = request.get_json()
        if not tournament_dict:
            response = {'message': 'No input provided'}
            return response, HttpStatus.bad_request_400.value

        errors = tournament_schema.validate(tournament_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value

        msg, creator_ok = Tournament.CheckCreatorExistsAndIsAnOfficial(User, tournament_dict['creator_id'])
        if not creator_ok:
            return {'message': msg}, HttpStatus.bad_request_400.value

        try:
            tournament = Tournament(
                tournament_dict['gametype'],
                tournament_dict['participants_num'],
                tournament_dict['creator_id']
            )
            tournament.add(tournament)
            query = Tournament.query.get(tournament.id)
            dumped_result = tournament_schema.dump(query)
            return dumped_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value


class UserPlayResource(Resource):
    def get(self, user_id, play_id):
        user_play = UserPlay.query.filter_by(user_id=user_id, play_id=play_id).first_or_404()
        dumped_user_play = user_play_schema.dump(user_play)
        return dumped_user_play


class UserPlaysResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        user_play = UserPlay.query.filter_by(user_id=user_id).first()
        dumped_result = user_play_schema.dump(user_play, many=True)
        return dumped_result


class UserPlayListResource(Resource):
    def get(self):
        user_plays = UserPlay.query.all()
        dumped_result = user_play_schema.dump(user_plays, many=True)
        return dumped_result

    def post(self):
        user_play_dict = request.get_json()
        
        if not user_play_dict:
            response = {'message': 'No input provided'}
            return response, HttpStatus.bad_request_400.value

        errors = user_play_schema.validate(user_play_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value

        user_exists = User.query.get(user_play_dict['user_id']) != None
        if not user_exists:
            return {'message': 'Invalid user_id.'}, HttpStatus.bad_request_400.value

        play_exists = Play.query.get(user_play_dict['play_id']) != None
        if not play_exists:
            return {'message': 'Invalid play_id'}, HttpStatus.bad_request_400.value

        user_play_exists = UserPlay.query.filter_by(user_id=user_play_dict['user_id'], play_id=user_play_dict['play_id']).first()
        if user_play_exists:
            return {'message': 'UserPlay with user_id {} and play_id {} already exists.'\
                .format(user_play_dict['user_id'], user_play_dict['play_id'])}, HttpStatus.bad_request_400.value

        if user_play_dict.get('tournament_id') != None:
            if user_play_dict.get('place') != None:
                tournament_exists = Tournament.query.get(user_play_dict['tournament_id']) != None
                if not tournament_exists:
                    return {'message': 'Invalid tournament_id.'}, HttpStatus.bad_request_400.value
        elif user_play_dict.get('place') != None:
            return {'message': 'UserPlay\'s place is only needed when they UserPlay belongs to a tournament.'}, HttpStatus.bad_request_400.value
        else:
            user_play_dict['tournament_id'] = None
            user_play_dict['place'] = None

        try:
            user_play = UserPlay(
                user_play_dict['user_id'],
                user_play_dict['play_id'],
                user_play_dict.get('tournament_id'),
                user_play_dict.get('place'),
                user_play_dict['result']
            )
            user_play.add(user_play)
            

            # Update Total Score
            total_score = UserTotalScore.query.get(user_play_dict['user_id'])
            if total_score == None:
                total_score = UserTotalScore(user_play_dict['user_id'])
            win = 1 if user_play_dict['result'] == "win" else 0
            lose = 1 if user_play_dict['result'] == "lose" else 0
            draw = 1 if user_play_dict['result'] == "draw" else 0

            if user_play_dict.get('tournament_id') == None:
                total_score.p_play_wins += win
                total_score.p_play_loses += lose
                total_score.p_play_wins += draw
            else:
                total_score.t_play_wins += win
                total_score.t_play_loses += lose
                total_score.t_play_wins += draw
            
            total_score.add(total_score)
            query = UserPlay.query.filter_by(user_id=user_play.user_id, play_id=user_play.play_id).first()
            dumped_result = user_play_schema.dump(query)
            return dumped_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value


class UserTotalScoreResource(Resource):
    @jwt_optional
    def get(self, play_mode):
        args = request.get_json()
        if args == None:
            return {"message": "No input given"}, HttpStatus.bad_request_400.value
        username = args.get('username')
        if username == None:
            return {"message": "username input given"}, HttpStatus.bad_request_400.value

        user = User.query.filter_by(username=username).first_or_404()
        score = UserTotalScore.query.get(user.id)

        if score == None:
            return {"message": "User {} does not have any score record.".format(username)}, HttpStatus.bad_request_400.value

        if play_mode not in ["practice", "tournament"]:
            return {"message": "invalid play_mode"}, HttpStatus.not_found_404.value
        
        total_score = {}
        total_score['username'] = user.username
        if play_mode == "practice":
            total_score['wins'] = score.p_play_wins
            total_score['loses'] = score.p_play_loses
            total_score['draws'] = score.p_play_draws
        elif play_mode == "tournament":
            total_score['wins'] = score.t_play_wins
            total_score['loses'] = score.t_play_loses
            total_score['draws'] = score.t_play_draws

        return total_score, HttpStatus.ok_200.value
            

class UserScoreListResource(Resource):
    @jwt_optional
    def get(self, play_mode):
        args = request.get_json()
        if args == None:
            return {"message": "No input given"}, HttpStatus.bad_request_400.value
        username = args.get('username')
        if username == None:
            return {"message": "username input given"}, HttpStatus.bad_request_400.value

        user = User.query.filter_by(username=username).first_or_404()
        if play_mode not in ["practice", "tournament"]:
            return '', HttpStatus.not_found_404.value


        userplay_table = UserPlay.__table__.name
        play_table = Play.__table__.name


        if play_mode == "practice":
            sql = text('select \'{}\', p.username, p.place, p.result, g.gametype from (select v.username, r.place, r.result, r.play_id from (select e.user_id as enemy_id, u.place as place, u.result as result, u.play_id as play_id from (select * from  public.user join {} on(id=user_id) where id={} and tournament_id is null) as u join (select * from {}) as e on (u.play_id=e.play_id) where u.user_id != e.user_id) as r join (select * from public.user) as v on (r.enemy_id=v.id)) as p join {} as g on (p.play_id=g.id)'\
                .format(user.username, userplay_table, user.id, userplay_table, play_table))
        elif play_mode == "tournament":
            sql = text('select \'{}\', p.username, p.place, p.result, g.gametype from (select v.username, r.place, r.result, r.play_id from (select e.user_id as enemy_id, u.place as place, u.result as result, u.play_id as play_id from (select * from  public.user join {} on(id=user_id) where id={} and tournament_id is not null) as u join (select * from {}) as e on (u.play_id=e.play_id) where u.user_id != e.user_id) as r join (select * from public.user) as v on (r.enemy_id=v.id)) as p join {} as g on (p.play_id=g.id)'\
                .format(user.username, userplay_table, user.id, userplay_table, play_table))

        result = orm.engine.execute(sql)
        play_list = []
        if play_mode == "practice":
            for z in result:
                ls = list(z)
                place = ls[2] if ls[2] != None else '-'
                play_list.append({'player1': ls[0], 'player2': ls[1], 'place': place, 'result': ls[3], 'gametype': ls[4]})
        elif play_mode == "tournament":
            for z in result:
                ls = list(z)
                place = ls[2] if ls[2] != None else '-'
                play_list.append({'player1': ls[0], 'player2': ls[1], 'place': place, 'result': ls[3], 'gametype': ls[4]})

        return {'play_list': play_list[::-1]}, HttpStatus.ok_200.value
        
        

#################
### RAM Views ###
#################

class ActivePlaysResource(Resource):
    def get(self):
        plays_json = gm.GetAllActivePlaysToJson()
        
        return plays_json, HttpStatus.ok_200.value


class PracticePlayJoinResource(Resource):
    @jwt_required
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value

        player_id = get_jwt_identity()
        gametype = args.get('gametype')
        ui_url = 'http://{}:{}/'.format(request.environ['REMOTE_ADDR'], 5000)


        if gametype == None:
            return {'message': 'gametype not given.'}, HttpStatus.bad_request_400.value
        if not GameType.Convertable(gametype):
            return {'message': 'invalid gametype {}'.format(gametype)}, HttpStatus.bad_request_400.value
        player = User.query.get(player_id)
        if not player:
            return {'message': 'Player with id {} doesn\'t exist.'.format(player_id)}, HttpStatus.bad_request_400.value
        gametype = GameType.FromStringToEnum(gametype)
        player_token_header = {'Authorization': dict(request.headers).get('Authorization')}
        username = get_jwt_claims().get('username')
        success = gm.AddPlayerInPracticePlayQueue(player_id, gametype, username, player_token_header, ui_url)
        if not success:
            return {'message': 'Failed to join practice play queue. Player already in queue or playing another game.'}, HttpStatus.precondition_failed_412.value
        return {'message': 'Successfully joined practice play queue'}, HttpStatus.ok_200.value



class OpenTournamentsResource(Resource):
    @jwt_required
    def get(self):
        args = request.get_json()
        if args != None:
            gametype = args.get('gametype')
            if gametype == None:
                tournaments_info = gm.GetOpenTournamentsInfo()
            elif GameType.Convertable(gametype):
                tournaments_info = gm.GetOpenTournamentsInfoOfGametype(GameType.FromStringToEnum(gametype))
            else:
                return {'message': 'invalid gametype: {}'.format(gametype)}, HttpStatus.bad_request_400.value
        else:
            tournaments_info = gm.GetOpenTournamentsInfo()

        info_jason = []
        for info in tournaments_info:
            info_jason.append(info.GetJsonRepresentation())

        return {'tournaments': info_jason}, HttpStatus.ok_200.value

    @jwt_required
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value

        user_claims = get_jwt_claims()
        participants_num = int(args.get('participants_num'))
        gametype = args.get('gametype')
        creator_id = get_jwt_identity()

        if user_claims['role'] != 'official':
            return {'message': 'Player/creator with id {} doesn\'t exist or is not an official.'.format(creator_id)}, HttpStatus.bad_request_400.value
        if participants_num == None:
            return {'message': 'participants_num field not given.'}, HttpStatus.bad_request_400.value
        if gametype == None:
            return {'message': 'gametype not given.'}, HttpStatus.bad_request_400.value
        if not GameType.Convertable(gametype):
            return {'invalid gametype {}'.format(gametype)}, HttpStatus.bad_request_400.value

        tour_info = gm.CreateTournament(participants_num, GameType.FromStringToEnum(gametype), creator_id)
        return {'tournament_info': tour_info.GetJsonRepresentation()}, HttpStatus.created_201.value

class OpenTournamentsRegisterResource(Resource):
    @jwt_required
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value

        tournament_id = args.get('tournament_id')
        player_id = get_jwt_identity()
        ui_url = 'http://{}:{}/'.format(request.environ['REMOTE_ADDR'], 5000)

        if tournament_id == None:
            return {'message': 'tournament_id not given.'}, HttpStatus.bad_request_400.value

        player = User.query.get(player_id)
        if not player:
            return {'message': 'Player with id {} doesn\'t exist.'.format(player_id)}, HttpStatus.bad_request_400.value

        player_token_header = {'Authorization': dict(request.headers).get('Authorization')}
        username = get_jwt_claims().get('username')
        if not gm.RegisterPlayerInTournament(player_id, tournament_id, username, player_token_header, ui_url):
            return {'message': 'Failed to register tournament {}. Tournament doesn\'t exist, or is full, or player is in another play'}, HttpStatus.precondition_failed_412.value
        return {'message': 'Successful register in tournament.'}, HttpStatus.ok_200.value
        

class PlayCreatedConfirmationResource(Resource):
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value
        
        play_id = args.get('play_id')

        if play_id == None:
            return {'message': 'play_id not given.'}, HttpStatus.bad_request_400.value

        play = Play.query.get(play_id)
        if play == None:
            return {'message': 'play with id {} doen\'t exist.'.format(play_id)}, HttpStatus.bad_request_400.value

        if not gm.ConfirmPlayCreation(play_id):
            return {'message': 'play with id {} doesn\'t need confirmation or it doesn\'t exist.'.format(play_id)}, HttpStatus.precondition_failed_412.value
        return {'message': 'The creation of play with id {} is confirmed'.format(play_id)}, HttpStatus.ok_200.value


class PlayResultUpdateResource(Resource):
    def post(self):
        args = request.get_json()
        if not args:
            return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value
        
        play_id = args.get('play_id')
        winner_id = args.get('winner_id')
        isADraw = args.get('isADraw')


        if play_id == None:
            return {'message': 'play_id not given.'}, HttpStatus.bad_request_400.value
        if isADraw == None:
            return {'message': 'isADraw not given.'}, HttpStatus.bad_request_400.value
        if winner_id == None and not isADraw:
            return {'message': 'winner_id not given.'}, HttpStatus.bad_request_400.value


        play_data = gm.FindActivePlay(play_id)

        if play_data == None:
            return {'message': 'Play with play_id {} not found'.format(play_id)}, HttpStatus.bad_request_400.value

        play_data.UpdatePlayResult(winner_id, isADraw)
        player1_id = play_data.player1
        player2_id = play_data.player2
        tournament_id = play_data.tournament_id
        phase = play_data.phase

        try:
            userplay1 = None
            userplay2 = None
            if isADraw:
                userplay1 = UserPlay(player1_id, play_id, tournament_id, None, "draw")
                userplay2 = UserPlay(player2_id, play_id, tournament_id, None, "draw")
            elif tournament_id != None:
                if phase == 2:
                    winner_place = 3
                    loser_place = 4
                elif phase == 1:
                    winner_place = 1
                    loser_place = 2
                else:
                    winner_place = None
                    loser_place = None
                userplay1 = UserPlay(play_data.GetWinner(), play_id, tournament_id, winner_place, "win")
                userplay2 = UserPlay(play_data.GetLoser(), play_id, tournament_id, loser_place, "lose")
            else:
                userplay1 = UserPlay(play_data.GetWinner(), play_id, None, None, "win")
                userplay2 = UserPlay(play_data.GetLoser(), play_id, None, None, "lose")

            userplay1.add(userplay1)
            userplay2.add(userplay2)

            gm.UpdatePlayResult(play_data)


            # Update Total Score
            player1_total_score = UserTotalScore.query.get(player1_id)
            player2_total_score = UserTotalScore.query.get(player2_id)
            # Create record if it doesnt exist
            if player1_total_score == None:
                player1_total_score = UserTotalScore(player1_id)
            
            if player2_total_score == None:
                player2_total_score = UserTotalScore(player2_id)

            p1_win = 1 if player1_id == winner_id else 0
            p1_lose = 1 if player2_id == winner_id else 0
            p1_draw = 1 if isADraw else 0

            p2_win = 1 if player2_id == winner_id else 0
            p2_lose = 1 if player1_id == winner_id else 0
            p2_draw = 1 if isADraw else 0

            if tournament_id == None:
                player1_total_score.p_play_wins += p1_win
                player1_total_score.p_play_loses += p1_lose
                player1_total_score.p_play_draws += p1_draw
                player2_total_score.p_play_wins += p2_win
                player2_total_score.p_play_loses += p2_lose
                player2_total_score.p_play_draws += p2_draw
            else:
                player1_total_score.t_play_wins += p1_win
                player1_total_score.t_play_loses += p1_lose
                player1_total_score.t_play_draws += p1_draw
                player2_total_score.t_play_wins += p2_win
                player2_total_score.t_play_loses += p2_lose
                player2_total_score.t_play_draws += p2_draw
            

            player1_total_score.add(player1_total_score)
            player2_total_score.add(player2_total_score)

            # If game or tournament is finished, delete it.
            p, i = gm.GetAndRemoveFinishedTournamentInfoAndFinishedPlays()

            return {'message': 'PlayerResult {} is updated successfully'.format(play_id)}, HttpStatus.created_201.value
        except SQLAlchemyError:
            orm.session.rollback()
            return {'message': 'PlayerResult {} failed to be updated.'.format(play_id)}, HttpStatus.bad_request_400.value


#############################
### UI-PlayMaster related ###
#############################

class PlayMasterHostResource(Resource):
    @jwt_required
    def get(self, play_id):
        play_master_url = gm.GetPlayMasterHostUrl(play_id)
        if play_master_url == None:
            return {}, HttpStatus.not_found_404.value
        else:
            return {'play_master_url': play_master_url}, HttpStatus.ok_200.value


class PlayerPlayMasterHostResource(Resource):
    @jwt_required
    def get(self, player_id):
        play_master_url = gm.GetPlayersGamePlayMasterHostUrl(player_id)
        if play_master_url == None:
            return {}, HttpStatus.not_found_404.value
        else:
            return {'play_master_url': play_master_url}, HttpStatus.ok_200.value

# PM -> GM related
class PlayHostResource(Resource):
    def post(self):
        data_dict = request.get_json()

        if data_dict == None:
            return {'message': 'no input'}, HttpStatus.bad_request_400.value

        play_ids = data_dict.get('play_ids')
        if play_ids == None:
            return {'message': 'play_ids not given'}, HttpStatus.bad_request_400.value

        pm_url = 'http://{}:{}/playmaster/'.format(request.environ['REMOTE_ADDR'], 5000)
        for play_id in play_ids:
            gm.SetPlayMasterHostUrl(play_id, pm_url)

        return {}, HttpStatus.ok_200.value


########################
### Resource Linking ###
########################

service.add_resource(PlayResource, '/plays/<int:play_id>')  # GET input: play_id
service.add_resource(PlayListResource, '/plays/')           # GET input: -, POST input: gametype

service.add_resource(TournamentResource, '/tournaments/<int:tournament_id>')    # GET input: tournament_id
service.add_resource(TournamentListResource, '/tournaments/')                   # GET input: -, POST input: gametype, participants_num, creator_id

service.add_resource(UserPlayResource, '/userplays/<int:user_id>/<int:play_id>')       # GET input: user_id/play_id
service.add_resource(UserPlaysResource, '/userplays/<int:user_id>')                    # GET input: user_id     
service.add_resource(UserPlayListResource, '/userplays/')                              # GET input: -, POST input: user_id, play_id, tournament_id(nullable), place(nullable), result

service.add_resource(UserTotalScoreResource, '/usertotalscore/<string:play_mode>')        #play_mode : [practice, tournament]  GET INPUT username
service.add_resource(UserScoreListResource, '/userscorelist/<string:play_mode>')          #play_mode : [practice, tournament]  GET INPUT username

# "RAM" views
service.add_resource(ActivePlaysResource, '/plays/active')
service.add_resource(PracticePlayJoinResource, '/practiceplay/join')
service.add_resource(OpenTournamentsResource, '/opentournaments/')
service.add_resource(OpenTournamentsRegisterResource, '/opentournaments/register')
service.add_resource(PlayCreatedConfirmationResource, '/plays/confirm')
service.add_resource(PlayResultUpdateResource, '/plays/result')

# ui-playmaster related
service.add_resource(PlayMasterHostResource, '/plays/<int:play_id>/host')
service.add_resource(PlayerPlayMasterHostResource, '/plays/player/<int:player_id>/host')
service.add_resource(PlayHostResource, '/plays/host')  # POST input: {play_ids: [play_id1, play_id2, ...]}
