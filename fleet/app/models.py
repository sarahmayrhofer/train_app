from fleet.run import db


class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    wagon_ids = db.Column(db.ARRAY(db.Integer), nullable=False)
    position = db.Column(db.String(50))

    def __repr__(self):
        return f"<Train(id={self.id}, name={self.name}, wagon_ids={self.wagon_ids}, position={self.position})>"


