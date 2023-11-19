from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, DateField, FloatField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Optional


class NewWagonForm(FlaskForm):
    wagon_type = SelectField('Wagon Typ', choices=[('locomotive', 'Triebwagen'),
                                                   ('normal_wagon', 'Wagon')], validators=[DataRequired()])
    track_width = SelectField('Spurweite', choices=[(1435, 'Normalspur (1435mm)'), (1000, 'Meterspur (1000mm)'),
                                                    (760, 'Schmalspur (7600mm)')], validators=[DataRequired()])
    train_id = IntegerField('Train ID', validators=[Optional()])
    max_traction = FloatField('Max. Zugkraft', validators=[Optional()])
    max_weight = FloatField('Max. Gewicht', validators=[Optional()])
    number_of_seats = IntegerField('Anz. an Sitzplätzen', validators=[Optional()])
    wagon_id = IntegerField( validators=[Optional()])
    submit = SubmitField('Bestätigen')


class NewMaintenanceForm(FlaskForm):
    description = StringField('Beschreibung', validators=[DataRequired()])
    start_date = DateField('Startdatum', validators=[DataRequired()])
    end_date = DateField('Enddatum', validators=[DataRequired()])
    assigned_employees = StringField('Zugewiesene Mitarbeiter', validators=[DataRequired()])
    submit = SubmitField('Bestätigen')


class NewTrainForm(FlaskForm):
    name = StringField('Zug Name', validators=[DataRequired()])
    position = StringField('Zug Position (optional)')

    selected_wagons = SelectMultipleField('Wagons auswählen', coerce=int, validators=[DataRequired()])
    selected_locomotive = SelectField('Triebfahrzeug auswählen', coerce=int, validators=[DataRequired()])

    submit = SubmitField('Bestätigen')
