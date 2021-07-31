from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import orm, User, UserTotalScore
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import (JWTManager, create_access_token)
import datetime

jwt = JWTManager()

def createAdminAccount():
    with app.app_context():
        username = "admin"
        password = "admin"
        role = "admin"

        try:
            admin_existing_acc = User.query.filter_by(username=username).first()
            if admin_existing_acc != None:
                return
            user = User(
                username,
                password,
                role,
                "token_wait_for_user_id"
            )
            user_claims = {'username': username, 'role': role}
            expires = datetime.timedelta(days=36500)
            user.add(user)
            query = User.query.get(user.id)
            query.token = create_access_token(query.id, user_claims=user_claims, expires_delta=expires)
            # Also Create UserTotalScoreTable
            user_total_score = UserTotalScore(user.id)
            user_total_score.add(user_total_score)
            orm.session.commit()
        except SQLAlchemyError:
            orm.session.rollback()



def create_app(config_filename):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "dontbesosecret"
    app.config.from_object(config_filename)
    jwt.init_app(app)
    orm.init_app(app)
    migrate = Migrate(app, orm)
    return app

app = create_app('config')
createAdminAccount()
