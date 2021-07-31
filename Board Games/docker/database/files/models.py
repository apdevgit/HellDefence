from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.apps import custom_app_context as password_context

orm = SQLAlchemy()
ma = Marshmallow()


class ResourceAddUpdateDelete():
    def add(self, resource):
        orm.session.add(resource)
        return orm.session.commit()

    def update(self):
        return orm.session.commit()

    def delete(self, resource):
        orm.session.delete(resource)
        return orm.session.commit()


##############################
### Authentication Service ###
##############################

USER_ROLES = ["player", "official", "admin"]


class User(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    username = orm.Column(orm.String(20), unique=True, nullable=False)
    password_hash = orm.Column(orm.String(), nullable=False)
    role = orm.Column(orm.String(10), nullable=False)
    token = orm.Column(orm.String(), nullable=False)


    def __init__(self, username, password, role, token):
        self.username = username
        self.password_hash = password_context.hash(password)
        self.role = role
        self.token = token

    def VerifyPassword(self, password):
        return password_context.verify(password, self.password_hash)

    def IsAnAdmin(self):
        return self.role == "admin"

    def IsAnOfficial(self):
        return self.role == "official"

    @classmethod
    def CheckUserName(cls, username):
        if(len(username) < 2):
            return 'Username must contain more than 1 characters.', False
        if(len(username) > 20):
            return 'Username must be less than 20 characters long.', False
        if(' ' in username):
            return 'Username must not contain white spaces', False
        return '', True

    @classmethod
    def CheckPassword(cls, password):
        if(len(password) < 6):
            return 'Password must be more than 5 characters long.', False
        if(len(password) > 32):
            return 'Password must be less than 33 characters long', False
        return '', True

    @classmethod
    def UsernameExists(cls, username):
        query_result = cls.query.filter_by(username=username).first()
        return query_result != None

class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(["player", "official", "admin"]))
    token = fields.String(dump_only=True)

##########################
### GameMaster Service ###
##########################

GAME_TYPES = ["tic-tac-toe", "chess"]
GAME_RESULTS = ["win", "lose", "draw", "canceled"]


class Play(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    gametype = orm.Column(orm.String(20), nullable=False)

    def __init__(self, gametype):
        self.gametype = gametype


class PlaySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    gametype = fields.String(required=True, validate=validate.OneOf(GAME_TYPES))


class Tournament(orm.Model, ResourceAddUpdateDelete):
    id = orm.Column(orm.Integer, primary_key=True)
    gametype = orm.Column(orm.String(20), nullable=False)
    participants_num = orm.Column(orm.Integer, nullable=False)
    creator_id = orm.Column(orm.Integer, orm.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, gametype, participants_num, creator_id):
        self.gametype = gametype
        self.participants_num = participants_num
        self.creator_id = creator_id

    @classmethod
    def CheckCreatorExistsAndIsAnOfficial(cls, user_model, user_id):
        user = user_model.query.get(user_id)
        if user == None:
            return 'Official with id {} doesn\'t exist.'.format(user_id), False
        elif not user.IsAnOfficial():
            return 'User with id {} is not an Offical.'.format(user_id), False
        return '', True


class TournamentSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    gametype = fields.String(required=True, validate=validate.OneOf(GAME_TYPES))
    participants_num = fields.Integer(required=True, validate=validate.Range(4, 128))   # TODO: ADD CHECK POWER OF 2
    creator_id = fields.Integer(required=True)


class UserPlay(orm.Model, ResourceAddUpdateDelete):
    user_id = orm.Column(orm.Integer, orm.ForeignKey('user.id'), primary_key=True)
    play_id = orm.Column(orm.Integer, orm.ForeignKey('play.id'), primary_key=True)
    tournament_id = orm.Column(orm.Integer, orm.ForeignKey('tournament.id'))
    place = orm.Column(orm.Integer)
    result = orm.Column(orm.String(20), nullable=False)

    def __init__(self, user_id, play_id, tournament_id, place, result):
        self.user_id = user_id
        self.play_id = play_id
        self.tournament_id = tournament_id
        self.place = place
        self.result = result

    @classmethod
    def UserIdIsValid(cls, user_model, user_id):
        user = user_model.query.get(user_id)
        return user != None

    @classmethod
    def PlayIdIsValid(cls, play_model, play_id):
        play = play_model.query.get(play_id)
        return play != None

class UserPlaySchema(ma.Schema):
    user_id = fields.Integer(required=True)
    play_id = fields.Integer(required=True)
    tournament_id = fields.Integer()
    place = fields.Integer(validate=validate.Range(1, 4))
    result = fields.String(required=True, validate=validate.OneOf(GAME_RESULTS))


class UserTotalScore(orm.Model, ResourceAddUpdateDelete):
    user_id = orm.Column(orm.Integer, orm.ForeignKey('user.id'), primary_key=True)
    p_play_wins = orm.Column(orm.Integer, nullable=False)
    p_play_loses = orm.Column(orm.Integer, nullable=False)
    p_play_draws = orm.Column(orm.Integer, nullable=False)
    t_play_wins = orm.Column(orm.Integer, nullable=False)
    t_play_loses = orm.Column(orm.Integer, nullable=False)
    t_play_draws = orm.Column(orm.Integer, nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        self.p_play_wins = 0
        self.p_play_loses = 0
        self.p_play_draws = 0
        self.t_play_wins = 0
        self.t_play_loses = 0
        self.t_play_draws = 0

class UserTotalScoreSchema(ma.Schema):
    user_id = fields.Integer(required=True)
    p_play_wins = fields.Integer(required=True)
    p_play_loses = fields.Integer(required=True)
    p_play_draws = fields.Integer(required=True)
    p_play_wins = fields.Integer(required=True)
    p_play_loses = fields.Integer(required=True)
    p_play_draws = fields.Integer(required=True)
