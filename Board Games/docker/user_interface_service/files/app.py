from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from http_status import HttpStatus
from flask_socketio import SocketIO, send, emit
from flask_jwt_extended import (JWTManager, jwt_required, jwt_optional, create_access_token, get_jwt_identity, get_jwt_claims, decode_token)
from ui_zookeeper_client import ZooKeeperUIClient
from spectate_manager import SpectateManager
import requests


jwt = JWTManager()

AUTHENTICATION_SERVICE_URL = None
PLAYMASTER_SERVICE_URL = None
GAMEMASTER_SERVICE_URL = None


def authentication_update_url_cb(url):
    global AUTHENTICATION_SERVICE_URL
    AUTHENTICATION_SERVICE_URL = url

def update_playmaster_url_cb(url):
    global PLAYMASTER_SERVICE_URL
    PLAYMASTER_SERVICE_URL = url

def update_gamemaster_url_cb(url):
    global GAMEMASTER_SERVICE_URL
    GAMEMASTER_SERVICE_URL = url


zkc = ZooKeeperUIClient(authentication_update_url_cb, update_gamemaster_url_cb)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dontbesosecret'
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
JWT_ACCESS_COOKIE_NAME = 'access_token'
app.config['KAZOO_HOSTS'] = 'zookeeper'
app.config['KAZOO_SESSION_TIMEOUT'] = 1
app.config['KAZOO_RETRY'] = {'max_tries': 600, 'delay': 1, 'backoff': 1,  'max_delay': 60}
socketio = SocketIO(app, cors_allowed_origins='*')
jwt.init_app(app)
zkc.init_app(app)


with app.app_context():
    try:
        zkc.Start()
    except:
        print("Terminating application. Cannot connect to zookeeper.")
        raise


sm = SpectateManager()
#/spectate/unregister/<int:play_id>

#PATH_EXTENSIONS = ['login', 'play_tic_tac_toe', 'play_chess', 'spectate_tic_tac_toe', 'spectate_chess', 'scores_practice', 'scores_tournament', 'create_tournament', 'create_account]

@app.route("/", defaults={"js": "login"})
@app.route("/<any(login, play, spectate, scores, create_tournament, create_account):js>")
def index(js):
    imd = request.args
    data = imd.to_dict()

    gametype = data.get('gametype')
    score_show = data.get('score_show')
    token = request.cookies.get('access_token')

    if gametype == None:
        gametype = 'tic-tac-toe'
    if score_show == None:
        score_show = 'practice'

    try:
        data = decode_token(token)
        claims = data['user_claims']
        logged_in = True
        username = claims['username']
        role = claims['role']
    except:
        logged_in = False
        username= ""
        role = "player"
        js = 'login' if js != 'spectate' else js
    
    if role != "admin" and js == 'create_account':
        js = 'play'
    elif role != "official" and js == 'create_tournament':
        js = 'play'

    return render_template("{0}.html".format(js), js=js, gametype=gametype, score_show=score_show, role=role, username=username, logged_in=logged_in)


@app.route("/auth/login", methods=["POST"])
def auth_login():
    login_dict = request.get_json()
    username = login_dict.get('username')
    password = login_dict.get('password')
    try:
        res = requests.post(AUTHENTICATION_SERVICE_URL + 'login', json={'username': username, 'password': password})
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    return res.json(), res.status_code

# TODO: Add optional JWT for role check
@app.route("/auth/register", methods=["POST"])
@jwt_optional
def auth_register():
    register_dict = request.get_json()
    username = register_dict.get('username')
    password = register_dict.get('password')
    role = register_dict.get('role')
    try:
        if get_jwt_identity() == None:
            res = requests.post(AUTHENTICATION_SERVICE_URL + "users/", json={'username': username, 'password': password, 'role': role})
        else:
            res = requests.post(AUTHENTICATION_SERVICE_URL + "users/", json={'username': username, 'password': password, 'role': role},\
                headers={'Authorization': dict(request.headers).get('Authorization')})
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    return res.json(), res.status_code

@app.route("/opentournaments/create", methods=["POST"])
@jwt_required
def create_open_tournament():
    tournament_dict = request.get_json()
    gametype = tournament_dict.get('gametype')
    participants_num = tournament_dict.get('participants_num')

    try:
        res = requests.post(GAMEMASTER_SERVICE_URL + "opentournaments/", json={'gametype': gametype, 'participants_num': participants_num},\
            headers={'Authorization': dict(request.headers).get('Authorization')})
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    return res.json(), res.status_code

@app.route("/opentournaments/<any(tic_tac_toe, chess):gametype>", methods=["GET"])
@jwt_required
def get_open_tournaments(gametype):
    gametype = 'tic-tac-toe' if gametype == 'tic_tac_toe' else gametype
    try:
        res = requests.get(GAMEMASTER_SERVICE_URL + "opentournaments/", json={'gametype': gametype}, headers={'Authorization': dict(request.headers).get('Authorization')})
    except Exception as e:
        print(str(e))
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    return res.json(), res.status_code

@app.route("/opentournaments/join", methods=["POST"])
@jwt_required
def join_open_tournament():
    join_dict = request.get_json()
    try:
        res = requests.post(GAMEMASTER_SERVICE_URL + "opentournaments/register", json={'tournament_id': join_dict.get('tournament_id')}, headers={'Authorization': dict(request.headers).get('Authorization')})
    except Exception as e:
        print(str(e))
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    return res.json(), res.status_code

@app.route("/games/join", methods=["POST"])  # input game type
@jwt_required
def join_game():
    data = request.get_json()
    if data == None:
        return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value
    gametype = data.get('gametype')
    try:
        res = requests.post(GAMEMASTER_SERVICE_URL + "practiceplay/join", json={'gametype': gametype}, \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        if res.status_code == HttpStatus.ok_200.value:
            return res.json(), res.status_code
        else:
            return '', res.status_code
    except requests.exceptions.RequestException:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    
        

@app.route("/games/tic-tac-toe/play", methods=["POST"])
@jwt_required
def play_tictactoe_move():
    data = request.get_json()
    if data == None:
        return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value

    play_id = data.get('play_id')
    square_to_play = data.get('square_to_play')
    play_master_url = None
    try:
        res = requests.get(GAMEMASTER_SERVICE_URL + "plays/{}/host".format(play_id), \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        if res.status_code != HttpStatus.ok_200.value:
            return res.json(), res.status_code
        play_master_url = res.json().get('play_master_url')
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    try:
        res = requests.post(play_master_url + "games/tic-tac-toe/{}/play".format(play_id), json={'square_to_play': square_to_play}, \
            headers={'Authorization': dict(request.headers).get('Authorization')})
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    if res.status_code == HttpStatus.ok_200.value:
        return res.json(), res.status_code
    else:
        return {'message': 'not found'}, res.status_code


@app.route("/games/chess/play", methods=["POST"])
@jwt_required
def play_chess_move():
    data = request.get_json()
    if data == None:
        return {'message': 'No input provided.'}, HttpStatus.bad_request_400.value

    play_id = data.get('play_id')
    square_from = data.get('square_from')
    square_to = data.get('square_to')

    play_master_url = None
    try:
        res = requests.get(GAMEMASTER_SERVICE_URL + "plays/{}/host".format(play_id), \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        if res.status_code != HttpStatus.ok_200.value:
            return res.json(), res.status_code
        play_master_url = res.json().get('play_master_url')
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value

    try:
        res = requests.post(play_master_url + "games/chess/{}/play".format(play_id), json={'square_from': square_from, 'square_to': square_to}, \
            headers={'Authorization': dict(request.headers).get('Authorization')})
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value
    if res.status_code == HttpStatus.ok_200.value:
        return res.json(), res.status_code
    else:
        return {'message': 'not found'}, res.status_code


# Check PlayMaster IP?
# Playmaster uses it to notify about gamestate changes
@app.route("/games/update", methods=["POST"])
@jwt_required
def receiveGameUpdate():
    data = request.get_json()
    if not data:
        return {'message', 'no input'}, HttpStatus.bad_request_400.value
    
    play_id = data.get('play_id')
    player1_id = data.get('player1_id')
    player2_id = data.get('player2_id')

    try:
        socketio.emit('spectate_' + str(player1_id), data)
        socketio.emit('spectate_' + str(player2_id), data)
        socketio.emit('spectate_game_' + str(play_id), data, namespace='/spectate')
    except:
        pass
    return '', HttpStatus.ok_200.value


# Returns game state if this player is in any game
@app.route("/games/updateforplayer")
@jwt_required
def getGameStateIfPlayerExists():
    try:
        res = requests.get(GAMEMASTER_SERVICE_URL + "plays/player/{}/host".format(get_jwt_identity()), \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        if res.status_code != HttpStatus.ok_200.value:
            return res.json(), res.status_code

        play_master_url = res.json().get('play_master_url')

        res = requests.get(play_master_url + "games/player/{}".format(get_jwt_identity()), \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        return res.json(), res.status_code
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value


@app.route("/games/updateforplay", methods=['GET', 'POST'])
@jwt_required
def getGameStateIfPlayExists():
    args = request.get_json()
    
    if args == None:
        return {'message:' 'no input'}, HttpStatus.bad_request_400.value
    play_id = args.get('play_id')
    try:
        res = requests.get(GAMEMASTER_SERVICE_URL + "plays/{}/host".format(play_id), \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        if res.status_code != HttpStatus.ok_200.value:
            return res.json, res.status_code

        play_master_url = res.json().get('play_master_url')

        res = requests.get(play_master_url + "games/{}".format(play_id), \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        
        return res.json(), res.status_code
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value


@app.route("/games/active")
@jwt_required
def getAllActivePlays():
    try:
        res = requests.get(GAMEMASTER_SERVICE_URL + "plays/active", \
            headers={'Authorization': dict(request.headers).get('Authorization')})
        return res.json(), res.status_code
    except:
        return {'message': 'Connection loss / request timeout'}, HttpStatus.request_timetout_408.value


##########################
### Context Processors ###
##########################

@app.context_processor
def total_score_processor():
    def total_score(username, score_show):
        try:
            res = requests.get(GAMEMASTER_SERVICE_URL + "usertotalscore/" + score_show, json={'username': username})
        except:
            return []

        if res.status_code == HttpStatus.ok_200.value:
            return [res.json()]
        return []
    return {"total_score":total_score}

@app.context_processor
def play_scores_processor():
    def play_scores(username, score_show):
        try:
            res = requests.get(GAMEMASTER_SERVICE_URL + "userscorelist/" + score_show, json={'username': username})
        except:
            return []
        
        if res.status_code == HttpStatus.ok_200.value:
            return res.json()['play_list']
        return []
    return {"play_scores":play_scores}



################
### SocketIO ###
################

@socketio.on('get_total_score_io')
def get_total_score_io(username, play_mode):
    res = requests.get(GAMEMASTER_SERVICE_URL + "usertotalscore/" + play_mode, json={'username': username})
    if res.status_code == HttpStatus.ok_200.value:
        emit('get_total_score_io', ['success', res.json()])
    else:
        emit('get_total_score_io', ['failed', ''])


@socketio.on('get_play_scores_io')
def get_play_scores_io(username, play_mode):
    res = requests.get(GAMEMASTER_SERVICE_URL + "userscorelist/" + play_mode, json={'username': username})
    if res.status_code == HttpStatus.ok_200.value:
        emit('get_play_scores_io', ['success', res.json()['play_list']])
    else:
        emit('get_play_scores_io', ['failed', ''])


@socketio.on('connect')
def socketio_client_connect():
    return True
    
@socketio.on('disconnect')
def socketio_client_discconnect():
    player_sid = request.sid
    sm.RemoveSpectator(player_sid)

    if sm.HasGamesToUnregister():
        for play_id in sm.GetGamesToUnregisterFromSpectate():
            try:
                res = requests.get(GAMEMASTER_SERVICE_URL + "plays/{}/host".format(play_id), \
                    headers={'Authorization': 'Bearer ' + sm.GetAValidToken()})
                if res.status_code != HttpStatus.ok_200.value:
                    return
                
                play_master_url = res.json().get('play_master_url')

                requests.post(play_master_url + "spectate/unregister/{}".format(play_id), \
                    headers={'Authorization': 'Bearer ' + sm.GetAValidToken()})
                sm.ConfirmGameIsUnregisteredAndDelete(play_id)
            except Exception as e:
                pass

@socketio.on('connect', namespace='/spectate')
def socketio_client_spectate_connect():
    return True

@socketio.on('disconnect', namespace='/spectate')
def socketio_client_spectate_disconnect():
    player_sid = request.sid
    sm.RemoveSpectator(player_sid)

    if sm.HasGamesToUnregister():
        for play_id in sm.GetGamesToUnregisterFromSpectate():
            try:
                res = requests.get(GAMEMASTER_SERVICE_URL + "plays/{}/host".format(play_id), \
                    headers={'Authorization': 'Bearer ' + sm.GetAValidToken()})
                if res.status_code != HttpStatus.ok_200.value:
                    return
                
                play_master_url = res.json().get('play_master_url')

                requests.post(play_master_url + "spectate/unregister/{}".format(play_id), \
                    headers={'Authorization': 'Bearer ' + sm.GetAValidToken()})
                sm.ConfirmGameIsUnregisteredAndDelete(play_id)
            except Exception as e:
                pass

@socketio.on('spectate', namespace='/spectate')
def socketio_spectate(play_id, access_token):
    try:
        decode_token(access_token)
        sm.AddSpectate(request.sid, play_id, access_token)
    except:
        pass



if __name__ == '__main__':
    socketio.run(app)


