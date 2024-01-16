from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User

from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired
from wtforms import SelectField



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')




class SaleForm(FlaskForm):
    discount = FloatField('Discount', validators=[DataRequired()])
    line = SelectField('Line', coerce=int)
    submit = SubmitField('Create Sale')

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

"""
#funtioniert
class SearchTicketForm(FlaskForm):
    #start_station = StringField('Start Station', validators=[DataRequired()])
    #end_station = StringField('End Station', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    submit = SubmitField('Search')

"""

# Update the form to include start and end stations
class SearchTicketForm(FlaskForm):
    date = StringField('Date', validators=[DataRequired()])
    start_station = StringField('Start Station', validators=[DataRequired()])
    end_station = StringField('End Station', validators=[DataRequired()])
    submit = SubmitField('Search')