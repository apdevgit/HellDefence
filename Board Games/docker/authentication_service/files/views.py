from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from http_status import HttpStatus
from models import orm, User, UserSchema, UserTotalScore
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import (JWTManager, jwt_required, jwt_optional, create_access_token, get_jwt_identity, get_jwt_claims, decode_token)
from auth_zookeeper_client import ZooKeeperAuthClient
import datetime

service_blueprint = Blueprint('auth', __name__)
user_schema = UserSchema()
service = Api(service_blueprint)

jwt = JWTManager()
zkc = ZooKeeperAuthClient()

############################
### Authentication Views ###
############################


class UserLoginResource(Resource):
    def post(self):
        login_dict = request.get_json()

        if login_dict == None:
            return {'message': 'No input given.'}, HttpStatus.bad_request_400.value

        if login_dict.get('username') == None:# or login_dict.get('username') == '':
            return {'message': 'No username given.'}, HttpStatus.bad_request_400.value
        if login_dict.get('password') == None:# or login_dict.get('password') == '':
            return {'message': 'No password given.'}, HttpStatus.bad_request_400.value

        user = User.query.filter_by(username=login_dict['username']).first()
        if user == None:
            return {'message': 'Wrong username.'}, HttpStatus.bad_request_400.value
        password_ok = user.VerifyPassword(login_dict['password'])
        if not password_ok:
            return {'message': 'Wrong password'}, HttpStatus.bad_request_400.value

        dumped_user = user_schema.dump(user)
        return dumped_user


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        dumped_user = user_schema.dump(user)
        return dumped_user



class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        dumped_result = user_schema.dump(users, many=True)
        return dumped_result

    @jwt_optional
    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'message': 'No input provided'}
            return response, HttpStatus.bad_request_400.value
        if user_dict.get('username') == None or user_dict.get('username') == '':
            return {'message': 'No username given.'}, HttpStatus.bad_request_400.value
        if user_dict.get('password') == None or user_dict.get('password') == '':
            return {'message': 'No password given.'}, HttpStatus.bad_request_400.value
        if user_dict.get('role') == None:
            return {'message': 'No role given.'}, HttpStatus.bad_request_400.value

        if get_jwt_identity() != None:
            creator_role = get_jwt_claims().get('role')
            if creator_role != 'admin' and user_dict.get('role') in ['official', 'admin']:
                return {'message': 'Only an admin can create other admin or officail account'}, HttpStatus.bad_request_400.value

        errors = user_schema.validate(user_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value

        msg, username_success = User.CheckUserName(user_dict['username'])
        if not username_success:
            return {'message': msg}, HttpStatus.bad_request_400.value

        msg, password_success = User.CheckPassword(user_dict['password'])
        if not password_success:
            return {'message': msg}, HttpStatus.bad_request_400.value

        username_exists = User.UsernameExists(user_dict['username'])
        if username_exists:
            response = {'username': 'Username {} already exists'.format(user_dict['username'])}
            return response, HttpStatus.bad_request_400.value

        try:
            user = User(
                user_dict['username'],
                user_dict['password'],
                user_dict['role'],
                "token_wait_for_user_id"
            )
            user_claims = {'username': user_dict['username'], 'role': user_dict['role']}
            expires = datetime.timedelta(days=36500)
            user.add(user)
            query = User.query.get(user.id)
            user.token = create_access_token(user.id, user_claims=user_claims, expires_delta=expires)
            # Also Create UserTotalScoreTable
            user_total_score = UserTotalScore(user.id)
            user_total_score.add(user_total_score)
            dumped_result = user_schema.dump(query)
            return dumped_result, HttpStatus.created_201.value

        except SQLAlchemyError as e:
            orm.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value


########################
### Resource Linking ###
########################

service.add_resource(UserLoginResource, '/login')           # GET input: username, password

service.add_resource(UserResource, '/users/<int:user_id>')
service.add_resource(UserListResource, '/users/')            #POST input: username, password, and role!with jwt_optional! see more:
                                                            # https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.jwt_optional
                                                            # GET input: -