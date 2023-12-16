from flask_wtf import FlaskForm
from werkzeug.routing import ValidationError
from wtforms import SubmitField, IntegerField, StringField, DateField, FloatField, SelectField, SelectMultipleField, \
    PasswordField, BooleanField
from wtforms.validators import DataRequired, Optional, Email, EqualTo

from app.models import User



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    role = SelectField('Rolle', choices=[('admin', 'Admin'), ('user', 'Mitarbeiter')], validators=[DataRequired()])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
