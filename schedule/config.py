import os

basedir = os.path.abspath(os.path.dirname(__file__))


# used for database handling of the fleet database
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'timetable.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
