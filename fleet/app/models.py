from fleet.run import db


class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    wagon_ids = db.Column(db.ARRAY(db.Integer), nullable=False)
    position = db.Column(db.String(50))

    def __repr__(self):
        return f"<Train(id={self.id}, name={self.name}, wagon_ids={self.wagon_ids}, position={self.position})>"


class Wagon(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    track_width = db.Column(db.Integer, nullable=False)
    wagon_type = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'wagon',
        'polymorphic_on': wagon_type
    }

    def __repr__(self):
        return f"<Wagon(id={self.id}, track_width={self.track_width}, wagon_type={self.wagon_type})>"


class Locomotive(Wagon):
    max_traction = db.Column(db.Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'locomotive',
    }

    def __repr__(self):
        return f"<Locomotive(id={self.id}, track_width={self.track_width}, max_traction={self.max_traction})>"


class NormalWagon(Wagon):
    max_weight = db.Column(db.Float, nullable=False)
    number_of_seats = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'normal_wagon',
    }

    def __repr__(self):
        return f"<NormalWagon(id={self.id}, track_width={self.track_width}, max_weight={self.max_weight}, number_of_seats={self.number_of_seats})>"
