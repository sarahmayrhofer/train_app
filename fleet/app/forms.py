from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, DateField
from wtforms.validators import DataRequired


class NewWagonForm(FlaskForm):
    track_width = IntegerField('Spurweite in mm', validators=[DataRequired()])
    max_weight = IntegerField('Maximales Gewicht (in t.)', validators=[DataRequired()])
    number_of_seats = IntegerField('Sitzplätze', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')


class NewMaintenanceForm(FlaskForm):
    description = StringField('Beschreibung', validators=[DataRequired()])
    start_date = DateField('Startdatum', validators=[DataRequired()])
    end_date = DateField('Enddatum', validators=[DataRequired()])
    assigned_employees = StringField('Zugewiesene Mitarbeiter', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')
