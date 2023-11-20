from .db import db

class Fahrtdurchführung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Fügen Sie hier weitere relevante Felder hinzu, z.B.:
    datum = db.Column(db.Date, nullable=False)
    zeit = db.Column(db.Time)
    zug_id = db.Column(db.Integer, db.ForeignKey('train.id'))
    start_station = db.Column(db.Integer)
    mitarbeiter_ids = db.Column(db.String)


    def __repr__(self):
        return f'<Fahrtdurchführung {self.id}>'
    
class Train(db.Model):
    __tablename__ = 'train'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Hier können Sie weitere Felder hinzufügen, z.B. Typ, Kapazität, etc.
    # Beispiel:
    # type = db.Column(db.String(50))
    # capacity = db.Column(db.Integer)

    # Beziehung zu Fahrtdurchführung
    fahrtdurchfuehrungen = db.relationship('Fahrtdurchführung', backref='train', lazy=True)

    def __repr__(self):
        return f'<Train {self.name}>'