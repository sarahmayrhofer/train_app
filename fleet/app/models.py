from fleet.run import db


class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"Train(id={self.id}, name={self.name})"
