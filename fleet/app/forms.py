from flask_wtf import FlaskForm
from werkzeug.routing import ValidationError
from wtforms import SubmitField, IntegerField, StringField, DateField, FloatField, SelectField, SelectMultipleField, \
    PasswordField, BooleanField
from wtforms.validators import DataRequired, Optional, Email, EqualTo

from fleet.app.models import User, Maintenance


class NewMaintenanceForm(FlaskForm):
    description = StringField('Beschreibung', validators=[DataRequired()])
    start_date = DateField('Enddatum', validators=[DataRequired()])
    end_date = DateField('Startdatum', validators=[DataRequired()])
    assigned_employees = SelectMultipleField('Mitarbeiter auswählen', coerce=int, validators=[DataRequired()])
    train_id = SelectField('Zug auswählen', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Bestätigen')

    def validate_assigned_employees(self, field):
        # Check if selected employees are already assigned to other maintenance tasks
        conflicting_maintenance = Maintenance.query.filter(
            Maintenance.start_date <= self.end_date.data,
            Maintenance.end_date >= self.start_date.data,
            Maintenance.assigned_employees.any(User.id.in_(field.data))
        ).first()

        if conflicting_maintenance:
            raise ValidationError('Ein oder mehrere Mitarbeiter sind bereits für eine andere Wartung eingeplant.')


class NewWagonForm(FlaskForm):
    wagon_type = SelectField('Wagon Typ', choices=[('locomotive', 'Triebwagen'),
                                                   ('normal_wagon', 'Wagon')], validators=[DataRequired()])
    track_width = SelectField('Spurweite', choices=[(1435, 'Normalspur (1435mm)'), (1000, 'Meterspur (1000mm)'),
                                                    (760, 'Schmalspur (7600mm)')], validators=[DataRequired()])
    train_id = IntegerField('Train ID', validators=[Optional()])
    max_traction = FloatField('Max. Zugkraft', validators=[Optional()])
    max_weight = FloatField('Max. Gewicht', validators=[Optional()])
    number_of_seats = IntegerField('Anz. an Sitzplätzen', validators=[Optional()])
    wagon_id = IntegerField(validators=[Optional()])
    submit = SubmitField('Bestätigen')


class NewTrainForm(FlaskForm):
    name = StringField('Zug Name', validators=[DataRequired()])
    position = StringField('Zug Position (optional)')
    price_per_km = FloatField('Preis pro Kilometer', validators=[])
    selected_wagons = SelectMultipleField('Wagons auswählen', coerce=int, validators=[DataRequired()])
    selected_locomotive = SelectField('Triebfahrzeug auswählen', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Bestätigen')


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
