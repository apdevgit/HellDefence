
import os


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
# Replace your_user_name with the user name you configured for the database
# Replace your_password with the password you specified for the database user
SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}:5432/{DB_NAME}".format(DB_USER="flaskuser", DB_PASS="zero", DB_ADDR="database", DB_NAME="board_games_db")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
