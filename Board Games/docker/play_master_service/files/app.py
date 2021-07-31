from flask import Flask
from playmaster import service_blueprint, jwt, zkc


def create_app(config_filename):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dontbesosecret'
    app.config['KAZOO_HOSTS'] = 'zookeeper'
    app.config['KAZOO_SESSION_TIMEOUT'] = 0.5
    app.config['KAZOO_RETRY'] = {'max_tries': 600, 'delay': 1, 'backoff': 1,  'max_delay': 60}
    app.config.from_object(config_filename)
    jwt.init_app(app)
    zkc.init_app(app)
    app.register_blueprint(service_blueprint, url_prefix='/playmaster')
    app.debug = True
    return app

app = create_app('config')

with app.app_context():
    try:
        zkc.Start()
    except:
        print("Terminating application. Cannot connect to zookeeper.")
        raise
