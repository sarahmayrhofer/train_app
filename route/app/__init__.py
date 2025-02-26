from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_restful import Api
from sqlalchemy import event
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

#This is a workaround for the sqlite3 foreign key problem. I made it that way.
@app.before_first_request
def setup():
    # Changes for Foreign Keys
    @event.listens_for(db.engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        logging.info("PRAGMA foreign_keys=ON command executed.")

migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models

from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_principal import Principal
from app.models import User, Role

# Flask-Principal
principals = Principal(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from app.resources import SectionListResource, StationListResource, EventListResource, LineListResource

# for Restful interface, the resources are defined in the resources.py file.
# When a GET request is made to one of these URL paths, the get method of the corresponding resource class is called.
api = Api(app)
api.add_resource(StationListResource, '/route/stations')
api.add_resource(SectionListResource, '/route/sections')
api.add_resource(EventListResource, '/route/events')
api.add_resource(LineListResource, '/route/lines')