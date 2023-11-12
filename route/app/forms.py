from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, TextAreaField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Station
from wtforms.validators import Regexp
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Bestätigen')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bitte verwenden Sie einen anderen Benutzernamen.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte verwenden Sie eine andere E-Mail-Adresse.')
            
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')  
    
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
    



class newStationAdminForm(FlaskForm):
    nameOfStation = StringField('Name des Bahnhofs', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    coordinates = StringField('Koordinaten', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')
             

class EditStationForm(FlaskForm):
    nameOfStation = StringField('Name des Bahnhofs', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    coordinates = StringField('Koordinaten', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')


class SectionForm(FlaskForm):
    startStation = SelectField('Start Bahnhof', coerce=int)
    endStation = SelectField('End Bahnhof', coerce=int)
    fee = FloatField('Entgelt', validators=[DataRequired()])
    distance = FloatField('Länge', validators=[DataRequired()])
    maxSpeed = IntegerField('Maximalgeschwindigkeit', validators=[DataRequired()])
    trackWidth = IntegerField('Spurweite in mm', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')


class EventForm(FlaskForm):
    section = IntegerField('Abschnitt', validators=[DataRequired()])
    endDate = DateField('Enddatum', format='%Y-%m-%d', validators=[DataRequired()])
    officialText = StringField('Offizieller Text', validators=[DataRequired()])
    internalText = StringField('Interner Text', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

            



class newStationAdminForm(FlaskForm):
    nameOfStation = StringField('Name des Bahnhofs', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    coordinates = StringField('Koordinaten', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')
             

class EditStationForm(FlaskForm):
    nameOfStation = StringField('Name des Bahnhofs', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    coordinates = StringField('Koordinaten', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')



class SectionForm(FlaskForm):
    startStation = SelectField('Start Bahnhof', coerce=int)
    endStation = SelectField('End Bahnhof', coerce=int)
    fee = FloatField('Entgelt', validators=[DataRequired()])
    distance = FloatField('Länge', validators=[DataRequired()])
    maxSpeed = IntegerField('Maximalgeschwindigkeit', validators=[DataRequired()])
    trackWidth = IntegerField('Spurweite in mm', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')

from wtforms.validators import Regexp

class EventForm(FlaskForm):
    section = SelectField('Abschnitt', coerce=int, validators=[DataRequired()])
    endDate = StringField('Enddatum (YYYY-MM-DD)', validators=[Regexp('^\d{4}-\d{2}-\d{2}$|^$', message="Invalid date format")])
    officialText = StringField('Offizieller Text', validators=[DataRequired()])
    internalText = StringField('Interner Text', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')



class EditLineForm(FlaskForm):
    new_name = StringField('Neuer Linienname:', validators=[DataRequired()])
    submit = SubmitField('Änderungen speichern')



class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password')
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Bestätigen')

    def populate_obj(self, user):
        self.username.data = user.username
        self.email.data = user.email
        

