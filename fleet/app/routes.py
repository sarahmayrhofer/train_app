from functools import wraps

from flask import redirect, url_for, flash
from flask import render_template
from flask import request
from flask_login import login_user, current_user, login_required
from werkzeug.urls import url_parse

from fleet.app import app, db
from fleet.app.forms import NewWagonForm, NewMaintenanceForm, NewTrainForm, LoginForm, RegistrationForm, NewUserForm, \
    EditWagonForm
from fleet.app.models import Locomotive, NormalWagon, Train, User, Wagon, Maintenance


@app.before_request
def before_request():
    print("Before Request")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Diese Seite ist nur für Administratoren zugänglich.", "warning")
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


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
@admin_required
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


@app.route('/editWagon/<int:wagon_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_wagon_by_id(wagon_id):
    wagon = Wagon.query.get(wagon_id)

    form = EditWagonForm()

    if form.validate_on_submit():

        print(form)
        setattr(wagon, 'max_traction', form.max_traction.data)
        setattr(wagon, 'max_weight', form.max_weight.data)
        setattr(wagon, 'number_of_seats', form.number_of_seats.data)

        db.session.commit()

        return redirect(url_for('index'))

    # Set form field values with wagon data
    print(wagon.wagon_type)
    form.wagon_type.data = getattr(wagon, 'wagon_type', None)
    form.max_traction.data = getattr(wagon, 'max_traction', None)
    form.max_weight.data = getattr(wagon, 'max_weight', None)
    form.number_of_seats.data = getattr(wagon, 'number_of_seats', None)

    return render_template('edit_wagon.html', page_name=f'Wagon: {wagon_id} bearbeiten', user=current_user,
                           form=form, wagon=wagon)


# Train by ID
@app.route('/trains/<int:train_id>')
@login_required
def train_by_id(train_id):
    train = Train.query.get(train_id)
    return render_template('train_details.html', page_name=f'Zug: {train.name}', user=current_user, train=train)


# Create a new train
@app.route('/newTrain', methods=['GET', 'POST'])
@login_required
@admin_required
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
            'name': f'[Wagen {wagon.id}] {wagon.number_of_seats} Sitzplätze ({wagon.max_weight} t.)  | {wagon.track_width}mm.',
            'type': 'normal_wagon',
        }
        existing_wagons.append(wagon_info)

    for wagon in locomotives:
        wagon_info = {
            'id': wagon.id,
            'name': f'[Wagen {wagon.id}] (max. {wagon.max_traction} t.)  | {wagon.track_width}mm.',
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


@app.route('/editTrain/<int:train_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_train(train_id):
    train = Train.query.get(train_id)

    # only get wagons that are not already assigned to a train
    wagons = NormalWagon.query.filter((NormalWagon.train_id.is_(None)) | (NormalWagon.train_id == train_id)).all()
    locomotives = Locomotive.query.filter((Locomotive.train_id.is_(None)) | (Locomotive.train_id == train_id)).all()

    existing_wagons = []
    existing_locomotives = []

    # loop over wagons to get their information
    for wagon in wagons:
        wagon_info = {
            'id': wagon.id,
            'name': f'[Wagen {wagon.id}] {wagon.number_of_seats} Sitzplätze ({wagon.max_weight} t.) | {wagon.track_width}mm.)',
            'type': 'normal_wagon',
        }
        existing_wagons.append(wagon_info)

    for wagon in locomotives:
        wagon_info = {
            'id': wagon.id,
            'name': f'[Wagen {wagon.id}] (max. {wagon.max_traction} t.)  | {wagon.track_width}mm.',
            'type': 'locomotive',
        }
        existing_locomotives.append(wagon_info)

    form = NewTrainForm()
    form.selected_wagons.choices = [(wagon['id'], wagon['name']) for wagon in existing_wagons]
    form.selected_locomotive.choices = [(wagon['id'], wagon['name']) for wagon in existing_locomotives]

    # Validate the form and update the train
    if form.validate_on_submit():
        train.name = form.name.data
        train.price_per_km = form.price_per_km.data

        selected_wagon_ids = form.selected_wagons.data
        selected_wagons = NormalWagon.query.filter(NormalWagon.id.in_(selected_wagon_ids)).all()

        selected_locomotive_id = form.selected_locomotive.data
        selected_locomotive = Locomotive.query.get(selected_locomotive_id)

        all_selected_wagons = selected_wagons + [selected_locomotive] if selected_locomotive else selected_wagons

        train.wagons = all_selected_wagons

        db.session.commit()

        return redirect(url_for('index'))

    # Pre-fill the form with data from the existing train
    form.name.data = train.name
    form.price_per_km.data = train.price_per_km

    # Populate selected_wagons and selected_locomotive based on existing train's wagons
    selected_wagons = [wagon.id for wagon in train.wagons if isinstance(wagon, NormalWagon)]
    selected_locomotive = [wagon.id for wagon in train.wagons if isinstance(wagon, Locomotive)][
        0] if train.wagons and any(isinstance(wagon, Locomotive) for wagon in train.wagons) else None

    form.selected_wagons.data = selected_wagons
    form.selected_locomotive.data = selected_locomotive

    return render_template('edit_train.html', page_name='Zug bearbeiten', user=current_user, form=form)


@app.route('/deleteTrain/<int:train_id>', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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
    users = User.query.all()

    return render_template('users.html', page_name='Userverwaltung', user=current_user, users=users)


@app.route('/newUser', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = NewUserForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.role = form.role.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

    return render_template('new_user.html', page_name='Neuen Benutzer anlegen', user=current_user, form=form)


# User by ID
@app.route('/users/<int:user_id>')
@login_required
@admin_required
def user_by_id(user_id):
    return f"User with ID {user_id}"


# Maintenance Overview
@app.route('/maintenances/')
@app.route('/maintenances')
@login_required
def maintenance_overview():
    maintenances = Maintenance.query.all()
    return render_template('maintenances.html', page_name='Wartungen', user=current_user, maintenances=maintenances)


# Maintenance by ID
@app.route('/maintenances/<int:maintenance_id>')
@login_required
def maintenance_by_id(maintenance_id):
    maintenance = Maintenance.query.get(maintenance_id)

    return render_template('maintenance.html', page_name='Wartung', user=current_user, maintenance=maintenance)


# Create a new maintenance task
@app.route('/newMaintenance', methods=['GET', 'POST'])
@login_required
@admin_required
def new_maintenance():
    form = NewMaintenanceForm()

    trains = Train.query.all()
    users = User.query.all()

    existing_trains = []
    existing_users = []

    # loop over trains to get their information
    for train in trains:
        train_info = {
            'id': train.id,
            'name': train.name,
        }
        existing_trains.append(train_info)

    # loop over users to get their information
    for user in users:
        user_info = {
            'id': user.id,
            'name': user.username,
            'role': user.role,
        }
        existing_users.append(user_info)

    # set choices for train_id and assigned_employees
    form = NewMaintenanceForm()
    form.train_id.choices = [(train['id'], train['name']) for train in existing_trains]
    form.assigned_employees.choices = [(user['id'], user['name']) for user in existing_users]

    # validate form and create new maintenance
    if form.validate_on_submit():
        tmp = form.assigned_employees.data
        assigned_employees = User.query.filter(User.id.in_(tmp)).all()

        train_id = Train.query.get(form.train_id.data)

        new_maintenance = Maintenance()
        new_maintenance.description = form.description.data
        new_maintenance.start_date = form.start_date.data
        new_maintenance.end_date = form.end_date.data
        new_maintenance.train_id = train_id.id
        new_maintenance.assigned_employees = assigned_employees

        db.session.add(new_maintenance)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_maintenance.html', page_name='Neue Wartung', user=current_user, form=form)


@app.route('/editMaintenance/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)

    form = NewMaintenanceForm(obj=maintenance)

    trains = Train.query.all()
    users = User.query.all()

    existing_trains = []
    existing_users = []
    # loop over trains to get their information
    for train in trains:
        train_info = {
            'id': train.id,
            'name': train.name,
        }
        existing_trains.append(train_info)

    # loop over users to get their information
    for user in users:
        user_info = {
            'id': user.id,
            'name': user.username,
            'role': user.role,
        }
        existing_users.append(user_info)

    form.train_id.choices = [(train['id'], train['name']) for train in existing_trains]
    form.assigned_employees.choices = [(user['id'], user['name']) for user in existing_users]

    # validate form and update maintenance
    if form.validate_on_submit():
        tmp = form.assigned_employees.data
        assigned_employees = User.query.filter(User.id.in_(tmp)).all()

        train_id = Train.query.get(form.train_id.data)

        maintenance.description = form.description.data
        maintenance.start_date = form.start_date.data
        maintenance.end_date = form.end_date.data
        maintenance.train_id = train_id.id
        maintenance.assigned_employees = assigned_employees

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_maintenance.html', page_name='Wartung bearbeiten', user=current_user, form=form,
                           maintenance=maintenance)


@app.route('/deleteMaintenance/<int:maintenance_id>', methods=['GET', 'POST'])
@admin_required
def delete_maintenance(maintenance_id):
    maintenance = Maintenance.query.get(maintenance_id)

    if maintenance:
        db.session.delete(maintenance)
        db.session.commit()

        flash(f'Wartung gelöscht!', 'success')
    else:
        flash('Fehler', 'error')

    return redirect(url_for('index'))


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
