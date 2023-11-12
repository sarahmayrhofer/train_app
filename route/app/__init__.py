from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_restful import Api
from sqlalchemy import event
from sqlalchemy.engine import Engine

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Änderungen für Foreign Keys (Der Befehl laut Moodle hat bei mir nicht funktioniert)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models

from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_principal import Principal
from app.models import User, Role


# Änderungen für Access-Control

# Flask-Principal
principals = Principal(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from app.resources import SectionListResource, StationListResource, StationResource, SectionResource, EventListResource, EventResource, LineListResource, LineResource


# Restful
api = Api(app)
api.add_resource(StationListResource, '/route/stations')
api.add_resource(StationResource, '/route/stations/<int:id>')
api.add_resource(SectionListResource, '/route/sections')
api.add_resource(SectionResource, '/route/sections/<int:id>')
api.add_resource(EventListResource, '/route/events')
api.add_resource(EventResource, '/route/events/<int:id>')
api.add_resource(LineListResource, '/route/lines')
api.add_resource(LineResource, '/route/lines/<int:id>')
