from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import orm, User, UserTotalScore
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import (JWTManager, create_access_token)
import datetime

jwt = JWTManager()


def create_app(config_filename):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "dontbesosecret"
    app.config.from_object(config_filename)
    jwt.init_app(app)
    orm.init_app(app)
    migrate = Migrate(app, orm)
    return app

app = create_app('config')
