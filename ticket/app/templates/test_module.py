from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User



import unittest
from __init__ import fetch_specific_stations, db, Station

class TestFetchSpecificStations(unittest.TestCase):
    def setUp(self):
        # Set up the database
        self.db = db
        self.db.create_all()

    def tearDown(self):
        # Tear down the database
        self.db.session.remove()
        self.db.drop_all()

    def test_fetch_specific_stations(self):
        # Call the function with some predefined inputs
        fetch_specific_stations('Station1', 'Station2')

        # Check if the stations were fetched and saved correctly
        station1 = Station.query.filter_by(nameOfStation='Station1').first()
        station2 = Station.query.filter_by(nameOfStation='Station2').first()
        self.assertIsNotNone(station1)
        self.assertIsNotNone(station2)

if __name__ == '__main__':
    unittest.main()