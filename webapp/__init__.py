import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'sdf09sdfmp'

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import rec
    app.register_blueprint(rec.bp)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'

    return app
