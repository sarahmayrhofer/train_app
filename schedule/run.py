from flask import Flask
from app.models import Train, Fahrtdurchführung
from app.routes import main
from config import Config
from app.db import db  # Importieren Sie die Datenbankinstanz
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # Initialisieren Sie die Datenbank mit der App

with app.app_context():
    db.create_all()

    # Prüfen, ob die Datenbank leer ist
    if not Train.query.first():
        # Erstellen Sie einige Züge
        zug1 = Train(name="Zug 1")
        zug2 = Train(name="Zug 2")
        db.session.add(zug1)
        db.session.add(zug2)

        # Erstellen Sie einige Fahrtdurchführungen
        fahrt1 = Fahrtdurchführung(datum=datetime(2023, 1, 1, 10, 0, 0), zug_id=zug1.id)
        fahrt2 = Fahrtdurchführung(datum=datetime(2023, 1, 2, 12, 0, 0), zug_id=zug2.id)
        fahrt3 = Fahrtdurchführung(datum=datetime(2023, 1, 5, 11, 0, 0), zug_id=zug1.id)
        fahrt4 = Fahrtdurchführung(datum=datetime(2023, 2, 15, 11, 0, 0), zug_id=zug1.id)
        db.session.add(fahrt1)
        db.session.add(fahrt2)
        db.session.add(fahrt3)
        db.session.add(fahrt4)

        db.session.commit()

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
