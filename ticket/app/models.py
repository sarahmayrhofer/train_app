from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    tickets = db.relationship('Ticket', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
      






@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lineForTheSale = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False)
    discount = db.Column(db.Float)

    sale_line_rel = db.relationship('Line', foreign_keys=[lineForTheSale])

    
class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nameOfStation = db.Column(db.String(64))
    address = db.Column(db.String(120))
    coordinates = db.Column(db.String(120))

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    startStation = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    endStation = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    fee = db.Column(db.Float)
    distance = db.Column(db.Float)
    maxSpeed = db.Column(db.Integer)
    trackWidth = db.Column(db.Integer)

    start_station_rel = db.relationship('Station', foreign_keys=[startStation])
    end_station_rel = db.relationship('Station', foreign_keys=[endStation])

    @property
    def sectionName(self):
        return f"{self.start_station_rel.nameOfStation} - {self.end_station_rel.nameOfStation}"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    endDate = db.Column(db.Date)
    officialText = db.Column(db.String(200))
    internalText = db.Column(db.String(200))

    section_rel = db.relationship('Section', backref=db.backref('events', lazy=True))

    def __repr__(self):
        return f'<Event {self.id}>'


# Association table
line_sections = db.Table('line_sections',
    db.Column('line_id', db.Integer, db.ForeignKey('line.id')),
    db.Column('section_id', db.Integer, db.ForeignKey('section.id'), nullable=False),
    db.Column('order', db.Integer)
)

class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nameOfLine = db.Column(db.String(64))
    sections = db.relationship('Section', secondary=line_sections, order_by="line_sections.c.order", backref=db.backref('lines', lazy='dynamic'))

    @property
    def startStation(self):
        if self.sections:
            return self.sections[0].start_station_rel
        return None

    @property
    def endStation(self):
        if self.sections:
            return self.sections[-1].end_station_rel
        return None

#Daten von Shedule

#fleet 

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=True)
    price_per_km = db.Column(db.Float, nullable=True)
    total_number_of_seats = db.Column(db.Integer, nullable=True, default=100)
    wagons = db.relationship('Wagon', backref='train', lazy=True)

    maintenances = db.relationship('Maintenance', backref='train', lazy=True)

    def total_max_weight(self):
        normal_wagons = NormalWagon.query.filter_by(train_id=self.id).all()
        total_max_weight = sum([wagon.max_weight for wagon in normal_wagons if wagon.max_weight is not None])
        return total_max_weight

    def total_number_of_seats(self):
        normal_wagons = NormalWagon.query.filter_by(train_id=self.id).all()
        total_number_of_seats = sum(
            [wagon.number_of_seats for wagon in normal_wagons if wagon.number_of_seats is not None])
        return total_number_of_seats

    def __repr__(self):
        return f"<Train(id={self.id}, name={self.name}, wagons={self.wagons}, position={self.position})>"

class Wagon(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    track_width = db.Column(db.Integer, nullable=False)
    wagon_type = db.Column(db.String(20))
    number_of_seats = db.Column(db.Integer, nullable=True, default=20)

    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'wagon',
        'polymorphic_on': wagon_type
    }

    def __repr__(self):
        return f"<Wagon(id={self.id}, track_width={self.track_width}, wagon_type={self.wagon_type})>"

class Locomotive(Wagon):
    max_traction = db.Column(db.Float, nullable=True)
    #number_of_seats = db.Column(db.Integer, nullable=True, default=20)

    __mapper_args__ = {
        'polymorphic_identity': 'locomotive',
    }

    def __repr__(self):
        return f"<Locomotive(id={self.id}, track_width={self.track_width}, max_traction={self.max_traction})>"

class NormalWagon(Wagon):
    max_weight = db.Column(db.Float, nullable=True)
    #number_of_seats = db.Column(db.Integer, nullable=True, default=40)

    __mapper_args__ = {
        'polymorphic_identity': 'normal_wagon',
    }

    def __repr__(self):
        return f"<NormalWagon(id={self.id}, track_width={self.track_width}, max_weight={self.max_weight}, number_of_seats={self.number_of_seats})>"

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    assigned_employees = db.relationship('User', secondary='maintenance_user_association', backref='maintenance',
                                         lazy='dynamic')

    train_id = db.Column(db.Integer, db.ForeignKey('train.id'))

    def __repr__(self):
        return f"<Maintenance(id={self.id}, description={self.description}, start_date={self.start_date}, end_date={self.end_date})>"

maintenance_user_association = db.Table('maintenance_user_association',
                                        db.Column('maintenance_id', db.Integer, db.ForeignKey('maintenance.id')),
                                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                        )





class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    zug_id = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    start_station = db.Column(db.String(64))
    end_station = db.Column(db.String(64))
    price = db.Column(db.Float)
    seat_reserved = db.Column(db.Boolean)
    seat_number = db.Column(db.Integer, default= None)
    status = db.Column(db.String(64))  # can be 'active', 'deleted', 'passed'

    def __repr__(self):
        return '<Ticket {}>'.format(self.id)




class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zug_id = db.Column(db.Integer, nullable=False)
    datum = db.Column(db.Date, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)




































# Ding von Markus
class RideBetweenTwoStations(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    end_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date, nullable=False)  # new attribute
    price = db.Column(db.Float, nullable=False)

    start_station_rel = db.relationship('Station', foreign_keys=[start_station_id])
    end_station_rel = db.relationship('Station', foreign_keys=[end_station_id])

    def __repr__(self):
        return f"<RideBetweenTwoStations(start={self.start_station_rel.nameOfStation}, end={self.end_station_rel.nameOfStation}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}, price={self.price})>"
    

    ##new model - not anymore
class Journey(db.Model):
    __tablename__ = 'journeys'
    id = db.Column(db.Integer, primary_key=True)
    start_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'))
    end_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'))
    date = db.Column(db.Date)
    available_seats = db.Column(db.Integer)
    price = db.Column(db.Float)

class Trainstation(db.Model):
    __tablename__ = 'stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    arrival_time = db.Column(db.DateTime)
    departure_time = db.Column(db.DateTime)
    journey_id = db.Column(db.Integer, db.ForeignKey('journeys.id'))