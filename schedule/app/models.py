from .db import db
from datetime import datetime

class Fahrtdurchführung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    zeit = db.Column(db.Time)
    endzeit = db.Column(db.Time)
    zug_id = db.Column(db.Integer)
    line = db.Column(db.Integer)
    mitarbeiter_ids = db.Column(db.String)
    preise = db.Column(db.String)  # Spalte für Preise
    bahnhof_ids = db.Column(db.String)  # Spalte für Bahnhof-IDs
    zeiten = db.Column(db.String)  # Spalte für Zeiten

    def __repr__(self):
        return f'<Fahrtdurchführung {self.id}>'