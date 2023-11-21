from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from fleet.app import db, login


class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=True)

    wagons = db.relationship('Wagon', backref='train', lazy=True)

    maintenances = db.relationship('Maintenance', backref='train', lazy=True)

    def total_max_weight(self):
        normal_wagons = NormalWagon.query.filter_by(train_id=self.id).all()
        total_max_weight = sum([wagon.max_weight for wagon in normal_wagons if wagon.max_weight is not None])
        return total_max_weight

    def total_number_of_seats(self):
        normal_wagons = NormalWagon.query.filter_by(train_id=self.id).all()
        total_number_of_seats = sum([wagon.number_of_seats for wagon in normal_wagons if wagon.number_of_seats is not None])
        return total_number_of_seats

    def __repr__(self):
        return f"<Train(id={self.id}, name={self.name}, wagons={self.wagons}, position={self.position})>"


class Wagon(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    track_width = db.Column(db.Integer, nullable=False)
    wagon_type = db.Column(db.String(20))

    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'wagon',
        'polymorphic_on': wagon_type
    }

    def __repr__(self):
        return f"<Wagon(id={self.id}, track_width={self.track_width}, wagon_type={self.wagon_type})>"


class Locomotive(Wagon):
    max_traction = db.Column(db.Float, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'locomotive',
    }

    def __repr__(self):
        return f"<Locomotive(id={self.id}, track_width={self.track_width}, max_traction={self.max_traction})>"


class NormalWagon(Wagon):
    max_weight = db.Column(db.Float, nullable=True)
    number_of_seats = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'normal_wagon',
    }

    def __repr__(self):
        return f"<NormalWagon(id={self.id}, track_width={self.track_width}, max_weight={self.max_weight}, number_of_seats={self.number_of_seats})>"


class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    assigned_employees = db.Column(db.String(255), nullable=True)

    train_id = db.Column(db.Integer, db.ForeignKey('train.id'))

    def __repr__(self):
        return f"<Maintenance(id={self.id}, description={self.description}, start_date={self.start_date}, end_date={self.end_date}, assigned_employees={self.assigned_employees})>"


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


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
