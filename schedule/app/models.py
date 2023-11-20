from .db import db

class Fahrtdurchführung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Fügen Sie hier weitere relevante Felder hinzu, z.B.:
    datum = db.Column(db.Date, nullable=False)
    zeit = db.Column(db.Time)
    endzeit = db.Column(db.Time)
    zug_id = db.Column(db.Integer, db.ForeignKey('train.id'))
    line = db.Column(db.Integer)
    mitarbeiter_ids = db.Column(db.String)
    preise = db.Column(db.String)  # Spalte für Preise
    bahnhof_ids = db.Column(db.String)  # Spalte für Bahnhof-IDs
    zeiten = db.Column(db.String)  # Spalte für Zeiten


    def __repr__(self):
        return f'<Fahrtdurchführung {self.id}>'
    
class Train(db.Model):
    __tablename__ = 'train'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Beziehung zu Fahrtdurchführung
    fahrtdurchfuehrungen = db.relationship('Fahrtdurchführung', backref='train', lazy=True)

    def __repr__(self):
        return f'<Train {self.name}>'