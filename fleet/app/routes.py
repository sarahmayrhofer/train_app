from flask import render_template

from fleet.app import app, db
from fleet.app.forms import NewWagonForm, NewMaintenanceForm
from fleet.app.models import Maintenance, Wagon

print("Imported routes")


@app.before_request
def before_request():
    print("Before Request")


# Index Page
@app.route('/')
@app.route('/index')
@app.route('/trains/')
@app.route('/trains')
def index():
    user = {'username': 'Tobias Schwap'}
    return render_template('overview.html', page_name='Übersicht', user=user)


@app.route('/newWagon', methods=['GET', 'POST'])
def new_wagon():
    form = NewWagonForm()
    if form.validate_on_submit():
        wagon = Wagon(track_width=form.track_width.data, max_weight=form.max_weight.data,
                      number_of_seats=form.number_of_seats.data)
        # db.session.add(wagon)
        # db.session.commit()
    user = {'username': 'Tobias Schwap'}
    return render_template('new_wagon.html', page_name='Neue Wartung', user=user, form=form)


# Train by ID
@app.route('/trains/<int:train_id>')
def train_by_id(train_id):
    user = {'username': 'Tobias Schwap'}
    return render_template('train_details.html', page_name='Zug: TODO', user=user)


# Users Page
@app.route('/users/')
@app.route('/users')
def users():
    user = {'username': 'Tobias Schwap'}
    return render_template('user_management.html', page_name='Userverwaltung', user=user)


# User by ID
@app.route('/users/<int:user_id>')
def user_by_id(user_id):
    return f"User with ID {user_id}"


# Maintenance Overview
@app.route('/maintenances/')
@app.route('/maintenances')
def maintenance_overview():
    user = {'username': 'Tobias Schwap'}
    return render_template('maintenances.html', page_name='Wartungen', user=user)


# Create a new maintenance task
@app.route('/newMaintenance', methods=['GET', 'POST'])
def new_maintenance():
    form = NewMaintenanceForm()
    if form.validate_on_submit():
        maintenance = Maintenance(description=form.description.data, start_date=form.start_date.data,
                                  end_date=form.end_date.data, assigned_employees=form.assigned_employees.data)
        print(maintenance)
        db.session.add(maintenance)
        db.session.commit()
        print("Added new maintenance")
    user = {'username': 'Tobias Schwap'}
    return render_template('new_maintenance.html', page_name='Neue Wartung', user=user, form=form)


# Maintenance by ID
@app.route('/maintenances/<int:maintenance_id>')
def maintenance_by_id(maintenance_id):
    return f"Maintenance with ID {maintenance_id}"
