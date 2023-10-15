from fleet.run import db


class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    # Store wagon IDs as a comma-separated string
    wagon_ids = db.Column(db.String, nullable=True)

    def __init__(self, name, wagon_ids=None):
        self.name = name
        self.wagon_ids = wagon_ids

    def get_wagon_ids(self):
        if self.wagon_ids:
            return [int(id) for id in self.wagon_ids.split(",")]
        else:
            return []

    def add_wagon_id(self, wagon_id):
        if not self.wagon_ids:
            self.wagon_ids = str(wagon_id)
        else:
            self.wagon_ids += f",{wagon_id}"

    def get_locomotive(self):
        wagon_ids = self.get_wagon_ids()
        if wagon_ids:
            return wagon_ids[0]
        else:
            return None

    def __repr__(self):
        return f"Train(id={self.id}, name={self.name})"
