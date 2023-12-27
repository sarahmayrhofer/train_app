from .db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Fahrtdurchführung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    zeit = db.Column(db.Time)
    endzeit = db.Column(db.Time)
    zug_id = db.Column(db.Integer)
    line = db.Column(db.Integer)
    mitarbeiter_ids = db.Column(db.String)
    preise = db.Column(db.String)  
    bahnhof_ids = db.Column(db.String)  
    zeiten = db.Column(db.String)  
    def __repr__(self):
        return f'<Fahrtdurchführung {self.id}>'
    
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    startStation = db.Column(db.Integer, nullable=False)
    endStation = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Float)
    distance = db.Column(db.Float)
    maxSpeed = db.Column(db.Integer)
    trackWidth = db.Column(db.Integer)
    streckenhalteplan_id = db.Column(db.Integer, db.ForeignKey('streckenhalteplan.id'))
    
class Streckenhalteplan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    start_station_id = db.Column(db.Integer)
    end_station_id = db.Column(db.Integer)
    original_line_id = db.Column(db.Integer)
    sections = db.relationship('Section', backref='streckenhalteplan')
    travel_duration = db.Column(db.Float)

    def calculate_travel_duration(self):
        self.travel_duration = sum([section.distance / section.maxSpeed for section in self.sections])


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), default="user")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return str(self.id)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
