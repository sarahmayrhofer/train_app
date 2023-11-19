from flask import render_template

from fleet.app import app, db
from fleet.app.forms import NewWagonForm, NewMaintenanceForm, NewTrainForm
from fleet.app.models import Maintenance, Locomotive, NormalWagon, Train

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

    locomotives = Locomotive.query.all()
    wagons = NormalWagon.query.all()

    trains = Train.query.all()

    return render_template('overview.html', page_name='Übersicht', user=user, wagons=wagons, locomotives=locomotives, trains=trains)


@app.route('/newWagon', methods=['GET', 'POST'])
def new_wagon():
    user = {'username': 'Tobias Schwap'}

    form = NewWagonForm()

    if form.validate_on_submit():
        if form.wagon_type.data == 'locomotive':
            wagon = Locomotive(track_width=form.track_width.data, max_traction=form.max_traction.data)
            db.session.add(wagon)
            db.session.commit()

        elif form.wagon_type.data == 'normal_wagon':
            wagon = NormalWagon(track_width=form.track_width.data, max_weight=form.max_weight.data,
                                number_of_seats=form.number_of_seats.data)
            db.session.add(wagon)
            db.session.commit()

    return render_template('new_wagon.html', page_name='Neuer Wagen', user=user, form=form)


# Train by ID
@app.route('/trains/<int:train_id>')
def train_by_id(train_id):
    user = {'username': 'Tobias Schwap'}
    return render_template('train_details.html', page_name='Zug: TODO', user=user)


# Create a new train
@app.route('/newTrain', methods=['GET', 'POST'])
def new_train():
    user = {'username': 'Tobias Schwap'}

    # only get wagons that are not already assigned to a train
    wagons = NormalWagon.query.filter_by(train_id=None).all()
    locomotives = Locomotive.query.filter_by(train_id=None).all()

    existing_wagons = []
    existing_locomotives = []

    # loop over wagons to get their information
    for wagon in wagons:
        wagon_info = {
            'id': wagon.id,
            'name': f'[Wagen {wagon.id}] {wagon.number_of_seats} Sitzplätze ({wagon.max_weight} t.)',
            'type': 'normal_wagon',
        }
        existing_wagons.append(wagon_info)

    for wagon in locomotives:
        wagon_info = {
            'id': wagon.id,
            'name': f'[Wagen {wagon.id}] (max. {wagon.max_traction} t.)',
            'type': 'locomotive',
        }
        existing_locomotives.append(wagon_info)

    form = NewTrainForm()
    form.selected_wagons.choices = [(wagon['id'], wagon['name']) for wagon in existing_wagons]
    form.selected_locomotive.choices = [(wagon['id'], wagon['name']) for wagon in existing_locomotives]

    if form.validate_on_submit():
        # Get selected normal wagons
        selected_wagon_ids = form.selected_wagons.data
        selected_wagons = NormalWagon.query.filter(NormalWagon.id.in_(selected_wagon_ids)).all()

        # Get selected locomotive
        selected_locomotive_id = form.selected_locomotive.data
        selected_locomotive = Locomotive.query.get(selected_locomotive_id)

        # Include the locomotive in the list of wagons
        all_selected_wagons = selected_wagons + [selected_locomotive] if selected_locomotive else selected_wagons

        # Create a new train and associate all selected wagons
        train = Train(name=form.name.data, wagons=all_selected_wagons)

        db.session.add(train)
        db.session.commit()

    return render_template('new_train.html', page_name='Neuer Zug', user=user, form=form)


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
