from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


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
    discount = db.Column(db.Float)

    
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

