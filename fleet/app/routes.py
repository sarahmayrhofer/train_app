from flask import redirect, url_for, flash
from flask import render_template
from flask import request
from flask_login import login_user, current_user, login_required
from werkzeug.urls import url_parse

from fleet.app import app, db
from fleet.app.forms import NewWagonForm, NewMaintenanceForm, NewTrainForm, LoginForm, RegistrationForm
from fleet.app.models import Maintenance, Locomotive, NormalWagon, Train, User, Wagon


@app.before_request
def before_request():
    print("Before Request")


# Index Page
@app.route('/')
@app.route('/index')
@app.route('/trains/')
@app.route('/trains')
@login_required
def index():
    locomotives = Locomotive.query.all()
    wagons = NormalWagon.query.all()

    trains = Train.query.all()

    return render_template('overview.html', page_name='Übersicht', user=current_user, wagons=wagons,
                           locomotives=locomotives,
                           trains=trains)


@app.route('/newWagon', methods=['GET', 'POST'])
@login_required
def new_wagon():
    form = NewWagonForm()

    if form.validate_on_submit():
        if form.wagon_type.data == 'locomotive':
            wagon = Locomotive(track_width=form.track_width.data, max_traction=form.max_traction.data)
            db.session.add(wagon)
            db.session.commit()
            return redirect(url_for('index'))

        elif form.wagon_type.data == 'normal_wagon':
            wagon = NormalWagon(track_width=form.track_width.data, max_weight=form.max_weight.data,
                                number_of_seats=form.number_of_seats.data)
            db.session.add(wagon)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('new_wagon.html', page_name='Neuer Wagen', user=current_user, form=form)


# Train by ID
@app.route('/trains/<int:train_id>')
@login_required
def train_by_id(train_id):
    train = Train.query.get(train_id)
    return render_template('train_details.html', page_name=f'Zug: {train.name}', user=current_user, train=train)


@app.route('/trains/<int:train_id>/edit')
@login_required
def edit_train_by_id(train_id):
    train = Train.query.get(train_id)
    return render_template('train_details.html', page_name=f'Zug: {train.name} bearbeiten', user=current_user,
                           train=train)


# Create a new train
@app.route('/newTrain', methods=['GET', 'POST'])
@login_required
def new_train():
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
        train.price_per_km = form.price_per_km.data

        db.session.add(train)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_train.html', page_name='Neuer Zug', user=current_user, form=form)


@app.route('/delete_train/<int:train_id>', methods=['GET', 'POST'])
def delete_train(train_id):
    train = Train.query.get(train_id)

    if train:
        db.session.delete(train)
        db.session.commit()

        flash(f'Zug {train.name} gelöscht!', 'success')
    else:
        flash('Fehler', 'error')

    return redirect(url_for('index'))


@app.route('/delete_wagon/<int:wagon_id>', methods=['GET', 'POST'])
def delete_wagon(wagon_id):
    wagon = Wagon.query.get(wagon_id)

    if wagon:
        db.session.delete(wagon)
        db.session.commit()

        flash(f'Wagen {wagon_id} gelöscht!', 'success')
    else:
        flash('Fehler', 'error')

    return redirect(url_for('index'))


# Users Page
@app.route('/users/')
@app.route('/users')
@login_required
def users():
    return render_template('user_management.html', page_name='Userverwaltung', user=current_user)


# User by ID
@app.route('/users/<int:user_id>')
@login_required
def user_by_id(user_id):
    return f"User with ID {user_id}"


# Maintenance Overview
@app.route('/maintenances/')
@app.route('/maintenances')
@login_required
def maintenance_overview():
    return render_template('maintenances.html', page_name='Wartungen', user=current_user)


# Create a new maintenance task
@app.route('/newMaintenance', methods=['GET', 'POST'])
@login_required
def new_maintenance():
    form = NewMaintenanceForm()
    if form.validate_on_submit():
        maintenance = Maintenance(description=form.description.data, start_date=form.start_date.data,
                                  end_date=form.end_date.data, assigned_employees=form.assigned_employees.data)
        print(maintenance)
        db.session.add(maintenance)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_maintenance.html', page_name='Neue Wartung', user=current_user, form=form)


# Maintenance by ID
@app.route('/maintenances/<int:maintenance_id>')
@login_required
def maintenance_by_id(maintenance_id):
    return f"Maintenance with ID {maintenance_id}"


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', page_name='Login', user=current_user, title='Sign In', form=form)


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', user=current_user, title='Register', form=form)
