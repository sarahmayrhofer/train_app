import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_restful import Api

from fleet.config import Config

# Create a Flask application instance
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# fixes: RuntimeError: A secret key is required to use CSRF
# https://stackoverflow.com/questions/47687307/how-do-you-solve-the-error-keyerror-a-secret-key-is-required-to-use-csrf-whe
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Import routes after initializing the Flask app and SQLAlchemy
from fleet.app import routes

from fleet.app.resources import AllTrainsResource

api = Api(app)
api.add_resource(AllTrainsResource, '/fleet/trains')
