
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, SaleForm
from app.models import Event, Locomotive, Maintenance, NormalWagon, RideBetweenTwoStations, Sale, Section, Train, User, Line, Wagon
from flask import request, redirect, url_for, render_template
from app import db
from app.models import Sale
from app.forms import SaleForm

from flask import flash
from app import db
from app.models import Station
from flask import redirect, url_for

import http.client
import json
from flask import flash
from app import db
from app.models import Station
import requests
import socket

from flask import request, jsonify
from . import app


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required



def index():
    posts = [
        {
            'author': {'username': 'Ticket App'},
            'body': 'Welcome!'
        },
        {
            'author': {'username': 'Ticket App'},
            'body': 'You can create discounts for different routes!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)



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
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)





@app.route('/create_sale', methods=['GET', 'POST'])
def create_sale():
    form = SaleForm()
    form.line.choices = [(line.id, line.nameOfLine) for line in Line.query.order_by('nameOfLine')]
    if form.validate_on_submit():
        sale = Sale(discount=form.discount.data, lineForTheSale=form.line.data)
        db.session.add(sale)
        db.session.commit()
        print(form.errors)
        return redirect(url_for('index'))
    return render_template('create_sale.html', form=form)



@app.route('/sales', methods=['GET'])
def sales():
    sales = Sale.query.all()
    lines = Line.query.all()
    return render_template('sales.html', sales=sales, lines=lines)



@app.route('/edit_sale/<int:id>', methods=['GET', 'POST'])
def edit_sale(id):
    sale = Sale.query.get_or_404(id)
    form = SaleForm()
    form.line.choices = [(line.id, line.nameOfLine) for line in Line.query.order_by('nameOfLine')]

    if form.validate_on_submit():
        sale.discount = form.discount.data
        sale.lineForTheSale = form.line.data
        db.session.commit()
        return redirect(url_for('sales'))

    elif request.method == 'GET':
        form.discount.data = sale.discount
        form.line.data = sale.lineForTheSale

    print(form.errors)  # print form errors

    return render_template('edit_sale.html', form=form)


@app.route('/delete_sale/<int:id>', methods=['POST'])
def delete_sale(id):
    sale = Sale.query.get_or_404(id)
    db.session.delete(sale)
    db.session.commit()
    return redirect(url_for('sales'))





# Routen zum Importieren der Daten Beginn


def fetch_and_save_stations():
    # Clear all stations
    Station.query.delete()

    conn = http.client.HTTPConnection("127.0.0.1", 5001)
    conn.request("GET", "/route/stations")
    response = conn.getresponse()

    if response.status != 200:
        flash('Failed to fetch stations: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    for station_data in data:
        station = Station(
            id=station_data['id'],
            nameOfStation=station_data['nameOfStation'],
            address=station_data['address'],
            coordinates=station_data['coordinates']
        )
        db.session.add(station)

    db.session.commit()
    flash('Stations fetched and saved successfully.')

def fetch_and_save_sections():
    # Clear all sections
    Section.query.delete()

    conn = http.client.HTTPConnection("127.0.0.1", 5001)
    conn.request("GET", "/route/sections")
    response = conn.getresponse()

    if response.status != 200:
        flash('Failed to fetch sections: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    for section_data in data:
        section = Section(
            id=section_data['id'],
            startStation=section_data['startStationId'],
            endStation=section_data['endStationId'],
            fee=section_data['fee'],
            distance=section_data['distance'],
            maxSpeed=section_data['maxSpeed'],
            trackWidth=section_data['trackWidth']
        )
        db.session.add(section)

    db.session.commit()
    flash('Sections fetched and saved successfully.')

def fetch_and_save_lines():
    # Clear all lines
    Line.query.delete()

    conn = http.client.HTTPConnection("127.0.0.1", 5001)
    conn.request("GET", "/route/lines")
    response = conn.getresponse()

    if response.status != 200:
        flash('Failed to fetch lines: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    for line_data in data:
        line = Line(
            id=line_data['id'],
            nameOfLine=line_data['nameOfLine'],
        )
        db.session.add(line)

        for section_data in line_data['sections']:
            section = Section.query.get(section_data['id'])
            if section:
                line.sections.append(section)

    db.session.commit()
    flash('Lines fetched and saved successfully.')

from datetime import datetime

def fetch_and_save_events():
    # Clear all events
    Event.query.delete()

    conn = http.client.HTTPConnection("127.0.0.1", 5001)
    conn.request("GET", "/route/events")
    response = conn.getresponse()

    if response.status != 200:
        flash('Failed to fetch events: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    for event_data in data:
        section = Section.query.get(event_data['sectionId'])
        if section is None:
            flash(f'Section with id {event_data["sectionId"]} not found.')
            continue

        endDate = datetime.strptime(event_data['endDate'], '%Y-%m-%d') if event_data['endDate'] else None

        event = Event(
            id=event_data['id'],
            section=section.id,
            endDate=endDate,
            officialText=event_data['officialText'],
            internalText=event_data['internalText'],
        )
        db.session.add(event)

    db.session.commit()
    flash('Events fetched and saved successfully.')

import requests
from datetime import datetime

def fetch_and_save_trains():
    response = requests.get("http://127.0.0.1:5002/fleet/trains")
    data = response.json()

    for train_data in data:
        train = Train.query.get(train_data['id'])
        if train is None:
            train = Train(id=train_data['id'])
            db.session.add(train)
        train.name = train_data['name']
        train.position = train_data['position']
        train.price_per_km = train_data['price_per_km']

        for wagon_data in train_data['wagons']:
            wagon = Wagon.query.get(wagon_data['id'])
            if wagon is None:
                if wagon_data['wagon_type'] == 'locomotive':
                    wagon = Locomotive(id=wagon_data['id'])
                else:
                    wagon = NormalWagon(id=wagon_data['id'])
                db.session.add(wagon)
            wagon.track_width = wagon_data['track_width']
            wagon.train = train

        for maintenance_data in train_data['maintenances']:
            maintenance = Maintenance.query.get(maintenance_data['id'])
            if maintenance is None:
                maintenance = Maintenance(id=maintenance_data['id'])
                db.session.add(maintenance)
            maintenance.description = maintenance_data['description']
            maintenance.train = train

    db.session.commit()



from flask import request
import requests
from datetime import datetime
from flask import request, abort
import requests
from datetime import datetime
import json

@app.route('/fetch_schedule', methods=['POST'])
def fetch_schedule():
    url = request.data.decode('utf-8')  # Get the URL of the API from the request body

    # Check if the URL is empty
    if not url:
        abort(400, description="Invalid URL")

    try:
        # Make a GET request to the API
        response = requests.get(url)
        data = response.json()
    except requests.exceptions.RequestException as e:
        abort(500, description="Error fetching data from API")

    # Loop through the data and create a new RideBetweenTwoStations object for each item
    for item in data:
        # Convert the dates and times from strings to datetime and date objects
        start_time = datetime.strptime(item['start_time'], '%Y-%m-%dT%H:%M:%S')
        end_time = datetime.strptime(item['end_time'], '%Y-%m-%dT%H:%M:%S')
        date = datetime.strptime(item['date'], '%Y-%m-%d').date()

        ride = RideBetweenTwoStations(
            start_station_id=item['start_station_id'],
            end_station_id=item['end_station_id'],
            start_time=start_time,
            end_time=end_time,
            date=date,
            price=item['price']
        )

        # Add the new RideBetweenTwoStations object to the session
        db.session.add(ride)

    # Commit the session to save the changes to the database
    db.session.commit()

    return 'Schedule fetched and imported successfully', 200



# Routen zum Importieren der Daten Ende
@app.route('/fetch_stations', methods=['POST'])
def fetch_stations():
    fetch_and_save_stations()
    fetch_and_save_sections()
    fetch_and_save_lines()
    fetch_and_save_events()
    fetch_and_save_trains()
    fetch_schedule()
    return redirect(url_for('index'))



"""
def get_fahrtdurchfuehrungen():
    conn = http.client.HTTPConnection("127.0.0.1", 5000)
    conn.request("GET", "/fahrtdurchfuehrungen/")
    response = conn.getresponse()
    
    if response.status != 200:
        print('Failed to fetch fahrtdurchfuehrungen: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    for fahrtdurchfuehrung_data in data:
        fahrtdurchfuehrung = Fahrtdurchführung(
            id=fahrtdurchfuehrung_data['id'],
            datum=datetime.strptime(fahrtdurchfuehrung_data['datum'], '%Y-%m-%d').date(),
            zeit=datetime.strptime(fahrtdurchfuehrung_data['zeit'], '%H:%M:%S').time(),
            endzeit=datetime.strptime(fahrtdurchfuehrung_data['endzeit'], '%H:%M:%S').time(),
            zug_id=fahrtdurchfuehrung_data['zug_id'],
            line=fahrtdurchfuehrung_data['line'],
            mitarbeiter_ids=fahrtdurchfuehrung_data['mitarbeiter_ids'],
            preise=fahrtdurchfuehrung_data['preise'],
            bahnhof_ids=fahrtdurchfuehrung_data['bahnhof_ids'],
            zeiten=fahrtdurchfuehrung_data['zeiten']
        )
        db.session.add(fahrtdurchfuehrung)

    db.session.commit()
    print('Fahrtdurchfuehrungen fetched and saved successfully.')   







def get_fahrtdurchfuehrungen():
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 5003)
        conn.request("GET", "/fahrtdurchfuehrungen/")
    except socket.gaierror as e:
        print(f'Address-related error connecting to server: {e}')
        return
    except ConnectionRefusedError as e:
        print(f'Connection refused: {e}')
        return
    except http.client.HTTPException as e:
        print(f'HTTP error occurred: {e}')
        return

    try:
        response = conn.getresponse()
    except http.client.HTTPException as e:
        print(f'HTTP response error: {e}')
        return

    if response.status != 200:
        print(f'Failed to fetch fahrtdurchfuehrungen: HTTP {response.status}')
        return

    try:
        data = json.loads(response.read().decode())
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
        return

    # Continue processing data...

    for fahrtdurchfuehrung_data in data:
        fahrtdurchfuehrung = Fahrtdurchfuehrung(
            id=fahrtdurchfuehrung_data['id'],
            datum=datetime.strptime(fahrtdurchfuehrung_data['datum'], '%Y-%m-%d').date(),
            zeit=datetime.strptime(fahrtdurchfuehrung_data['zeit'], '%H:%M:%S').time(),
            endzeit=datetime.strptime(fahrtdurchfuehrung_data['endzeit'], '%H:%M:%S').time(),
            zug_id=fahrtdurchfuehrung_data['zug_id'],
            line=fahrtdurchfuehrung_data['line'],
            mitarbeiter_ids=fahrtdurchfuehrung_data['mitarbeiter_ids'],
            preise=fahrtdurchfuehrung_data['preise'],
            bahnhof_ids=fahrtdurchfuehrung_data['bahnhof_ids'],
            zeiten=fahrtdurchfuehrung_data['zeiten']
        )
        db.session.add(fahrtdurchfuehrung)

    db.session.commit()
    print('Fahrtdurchfuehrungen fetched and saved successfully.')   

"""


"""

if __name__ == '__main__':
    print('Starting application with app.run()')
    app.run(port=5003)

"""

#get_fahrtdurchfuehrungen()  # Call the function here


#neu suchen



@app.route('/search', methods=['GET'])
def search():
    start_id = request.args.get('start_id', type=int)
    end_id = request.args.get('end_id', type=int)

    # Load data from the /timetable endpoint
    conn = http.client.HTTPConnection("127.0.0.1", 5000)
    conn.request("GET", "/timetable")
    response = conn.getresponse()

    if response.status != 200:
        print('Failed to fetch timetable: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    # Search the data for entries that contain the start_id and end_id
    result = [d for d in data if start_id in d['bahnhof_ids'] and end_id in d['bahnhof_ids']]

    return jsonify(result)


def fetch_specific_stations(station1, station2):
    conn = http.client.HTTPConnection("127.0.0.1", 5001)
    conn.request("GET", "/route/stations")
    response = conn.getresponse()

    if response.status != 200:
        flash('Failed to fetch stations: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    specific_stations = [station for station in data if station['nameOfStation'] in [station1, station2]]

    for station_data in specific_stations:
        station = Station(
            id=station_data['id'],
            nameOfStation=station_data['nameOfStation'],
            address=station_data['address'],
            coordinates=station_data['coordinates']
        )
        db.session.add(station)

    db.session.commit()
    flash('Stations ' + station1 + ' and ' + station2 + ' fetched and saved successfully.')

"""
def get_fahrtdurchfuehrungen1(station1_id, station2_id):
    conn = http.client.HTTPConnection("127.0.0.1", 5000)
    conn.request("GET", "/fahrtdurchfuehrungen/")
    response = conn.getresponse()

    if response.status != 200:
        print('Failed to fetch fahrtdurchfuehrungen: HTTP ' + str(response.status))
        return

    data = json.loads(response.read().decode())

    for fahrtdurchfuehrung_data in data:
        # Check if both station IDs are in the 'bahnhof_ids' list
        if station1_id in fahrtdurchfuehrung_data['bahnhof_ids'] and station2_id in fahrtdurchfuehrung_data['bahnhof_ids']:
            fahrtdurchfuehrung = Fahrtdurchfuehrung(
                id=fahrtdurchfuehrung_data['id'],
                datum=datetime.strptime(fahrtdurchfuehrung_data['datum'], '%Y-%m-%d').date(),
                zeit=datetime.strptime(fahrtdurchfuehrung_data['zeit'], '%H:%M:%S').time(),
                endzeit=datetime.strptime(fahrtdurchfuehrung_data['endzeit'], '%H:%M:%S').time(),
                zug_id=fahrtdurchfuehrung_data['zug_id'],
                line=fahrtdurchfuehrung_data['line'],
                mitarbeiter_ids=fahrtdurchfuehrung_data['mitarbeiter_ids'],
                preise=fahrtdurchfuehrung_data['preise'],
                bahnhof_ids=fahrtdurchfuehrung_data['bahnhof_ids'],)
   
@app.route('/fetch_railstation_form', methods=['GET'])
def fetch_railstation_form():
    return render_template('fetch_railstation_form.html')

@app.route('/fetch_railstation', methods=['POST'])
def fetch_stations():
    station1 = request.form.get('station1')
    station2 = request.form.get('station2')
    fetch_and_save_stations(station1, station2)
    return redirect(url_for('index'))

"""