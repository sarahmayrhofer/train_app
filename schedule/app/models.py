from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime

"""
IMPORTANT: I use Nullable=false to make sure that the foreign keys are not null. in some cases, this is not what we want.
"""
    
 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
        
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Theoretisch könnte man auch eine vordefinierte funktion "has_role" nutzen, aber da wusst ich nicht, wie man die importiert.
    def check_is_admin(user):
        return Role.query.filter_by(name='admin').first() in user.roles
    
    def check_is_employee(user):
        return Role.query.filter_by(name='employee').first() in user.roles

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))    
            
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


    
class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nameOfStation = db.Column(db.String(64))
    address = db.Column(db.String(120))
    coordinates = db.Column(db.String(120))
 
# das ist eine funktion, die die id mit führenden nullen ausgibt. die brauchen wir später zum exportieren in die Schnittstellendatei. zfill füllt mit nullen auf. das @property ist ein decorator, der die funktion als attribut ausgibt. 
    @property
    def externId(self):
        return str(self.id).zfill(4)

    def __repr__(self):
        return '<Station {}>'.format(self.nameOfStation)       
        
        
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



# There, the foreign keys should be nullable
class ChosenSectionsForNewLine(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    order = db.Column(db.Integer)

    section_rel = db.relationship('Section', backref=db.backref('chosen_sections_for_new_line', lazy=True))


# There, the foreign keys should be nullable
class AvailableSectionsForNewLine(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))

    section_rel = db.relationship('Section', backref=db.backref('available_sections_for_new_line', lazy=True))