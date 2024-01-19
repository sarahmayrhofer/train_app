from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import Fahrtdurchführung, User
from app.routes import main
from app.db import db  
from datetime import datetime
#import os
#from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app) 

with app.app_context():
    db.create_all()
    #db.session.execute(text('DROP TABLE IF EXISTS fahrtdurchführung'))


    # Prüfen, ob die Datenbank leer ist
    if not Fahrtdurchführung.query.first():
        # Erstellen von Fahrtdurchführungen
        fahrt1 = Fahrtdurchführung(datum=datetime(2023, 1, 1, 10, 0, 0))
        fahrt2 = Fahrtdurchführung(datum=datetime(2023, 1, 2, 12, 0, 0))
        fahrt3 = Fahrtdurchführung(datum=datetime(2023, 1, 5, 11, 0, 0))
        fahrt4 = Fahrtdurchführung(datum=datetime(2023, 2, 15, 11, 0, 0))
        db.session.add(fahrt1)
        db.session.add(fahrt2)
        db.session.add(fahrt3)
        db.session.add(fahrt4)

        db.session.commit()

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
