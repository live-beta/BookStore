from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from config import configset, expiry_time

# application url accessibility between app and test

api_blue_print = Blueprint("api", __name__, url_prefix="/api/v1")
#initialise the Api class
api = Api(api_blue_print)
#Initialising SQL alchemy
db = SQLAlchemy()

def create_app(config_set):
    """
    Initialisation and setting up of config file settings

    """
    app = Flask(__name__)
    app.config.from_object(configset[config_set])
    configset[config_set].init_app(app)

    db.init_app(app)
    app.register_blueprint(api_blue_print)

    return app
