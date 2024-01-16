
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
from app import db

from flask import request

#new
from app.models import Journey, Trainstation

from flask import request, jsonify

from .forms import SearchTicketForm
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



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
        #
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#eine Fahrtstrecke, Fahrtverbindungen, errechne Preis, Aktion, 
#daten erweitern, zweite Strecke, Rabatt auf alle, 

#current user setzen, 

#Wien Hbf -> St. Pölten Hbf -> Linz Hbf -> Wels Hbf
#direkten

travelroutes = {
    "travel_id": 1,
    "name": "Westbahnstrecke", 
    "sections": [
        {
            "id": 1,
            "start_station_id": 1,
            "end_station_id": 2,
            "price": 10,
            "duration": 100,
        },
        {
            "id": 2,
            "start_station_id": 2,
            "end_station_id": 3,
            "fee": 10,
            "distance": 100,
        },
        {
            "id": 3,
            "start_station_id": 3,
            "end_station_id": 4,
            "fee": 10,
            "distance": 100,
        },
     
    ]
}

"""
Wien Hbf -> St. Pölten Hbf
Wien Hbf -> Linz Hbf
Wien Hbf -> Wels Hbf
St. Pölten Hbf -> Linz Hbf
St. Pölten Hbf -> Wels Hbf
Linz Hbf -> Wels Hbf
"""

#lassen sich von routes ableiten
connections = [
    {
        "id": 1,
        "start_station_id": 1,
        "start_station_name": "Wien Hbf",
        "end_station_id": 2,
        "end_station_name": "St. Pölten Hbf",
        "route_id": 1,
    },
    {
        "id": 2,
        "start_station_id": 1,
        "start_station_name": "Wien Hbf",
        "end_station_id": 3,
        "end_station_name": "Linz Hbf",
        "route_id": 1,
    },
    {
        "id": 3,
        "start_station_id": 1,
        "start_station_name": "Wien Hbf",
        "end_station_id": 4,
        "end_station_name": "Wels Hbf",
        "route_id": 1,
    },
    {
        "id": 4,
        "start_station_id": 2,
        "start_station_name": "St. Pölten Hbf",
        "end_station_id": 3,
        "end_station_name": "Linz Hbf",
        "route_id": 1,
    },
    {
        "id": 5,
        "start_station_id": 2,
        "start_station_name": "St. Pölten Hbf",
        "end_station_id": 4,
        "end_station_name": "Wels Hbf",
        "route_id": 1,
    },
    {
        "id": 6,
        "start_station_id": 3,
        "start_station_name": "Linz Hbf",
        "end_station_id": 4,
        "end_station_name": "Wels Hbf",
        "route_id": 1,
    }
]

#generelle Strecke, Connection - örtliche Abfrage, von bis, gibt es das?, bestimmte Zeit Durchführung, Trips, 

trips = [
    {
        "id": 1,
        "name": "L",
        "arrival_time": "2022-12-02T08:00:00",
        "departure_time": "2022-12-01T08:30:00",
        "route_id": 1
    },
    {
        "id": 2,
        "name": "S",
        "arrival_time": "2022-12-01T09:00:00",
        "departure_time": "2022-12-01T09:30:00",
        "route_id": 1
    },
    {
        "id": 3,
        "name": "Y",
        "arrival_time": "2022-12-01T10:00:00",
        "departure_time": "2022-12-01T10:30:00",
        "route_id": 1
    },
    {
        "id": 4,
        "name": "Wien",
        "arrival_time": "2022-12-01T11:00:00",
        "departure_time": "2022-12-01T11:30:00",
        "route_id": 1
    },
    {
        "id": 5,
        "name": "Linz",
        "arrival_time": "2022-12-02T08:00:00",
        "departure_time": "2022-12-02T08:30:00",
        "route_id": 1
    },
    {
        "id": 6,
        "name": "Z",
        "arrival_time": "2022-12-02T09:00:00",
        "departure_time": "2022-12-02T09:30:00",
        "route_id": 1
    },
    {
        "id": 7,
        "name": "K",
        "arrival_time": "2022-12-02T10:00:00",
        "departure_time": "2022-12-02T10:30:00",
        "route_id": 1
    },
    {
        "id": 8,
        "name": "Wien",
        "arrival_time": "2022-12-02T11:00:00",
        "departure_time": "2022-12-02T11:30:00",
        "route_id": 1
    },
    {
        "id": 9,
        "name": "Linz",
        "arrival_time": "2022-12-01T12:00:00",
        "departure_time": "2022-12-01T12:30:00",
        "route_id": 1
    }
]


"""
bahnhoefe = [
    {"name": "Linz", "id": 1},
    {"name": "Wien", "id": 2}
]
"""



def get_trips_by_date_and_time(trips, date, time):
    # Combine date and time into a datetime string
    datetime_str = f"{date}T{time}"
    
    # Convert the datetime string into a datetime object
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")

    # Filter the trips that have an arrival time greater than or equal to the given datetime
    filtered_trips = [trip for trip in trips if datetime.strptime(trip['arrival_time'], "%Y-%m-%dT%H:%M:%S") >= datetime_obj]

    return filtered_trips



@app.route('/journeys', methods=['GET'])
def get_all_journeys():
    return jsonify(journeys)    



@app.route('/journey', methods=['GET'])
def get_journey():
    start_station_name = request.args.get('start_station')
    end_station_name = request.args.get('end_station')
    date = request.args.get('date')
    time = request.args.get('time')

    # Check if all parameters are provided
    if not all([start_station_name, end_station_name, date, time]):
        return jsonify({'error': 'Missing parameters'}), 400

    # Convert date and time to datetime object for comparison
    datetime_str = date + 'T' + time
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')

    print(f"Searching for journeys from {start_station_name} to {end_station_name} on {date} after {time}")

    # Filter stations based on start_station, end_station, date and time
    start_stations = [station for station in stations if station['name'] == start_station_name and station.get('departure_time') and datetime.strptime(station['departure_time'], '%Y-%m-%dT%H:%M:%S') >= datetime_obj]
    end_stations = [station for station in stations if station['name'] == end_station_name and datetime.strptime(station['arrival_time'], '%Y-%m-%dT%H:%M:%S') >= datetime_obj]

    print(f"Found {len(start_stations)} start stations and {len(end_stations)} end stations")

    # Find journeys that match the filtered stations and the requested date
    matching_journeys = [journey for journey in journeys if journey['date'] == date and any(station['journey_id'] == journey['id'] for station in start_stations) and any(station['journey_id'] == journey['id'] for station in end_stations)]

    # For each matching journey, find the stations that are between the start and end stations
    for journey in matching_journeys:
        journey_stations = [station for station in stations if station['journey_id'] == journey['id'] and datetime.strptime(station['departure_time'], '%Y-%m-%dT%H:%M:%S') >= datetime_obj and datetime.strptime(station['arrival_time'], '%Y-%m-%dT%H:%M:%S') <= datetime_obj]
        journey['stations'] = journey_stations

    print(f"Found {len(matching_journeys)} matching journeys")

    return jsonify(matching_journeys)


#route markus extra!! 
@app.route('/test', methods=['GET'])
def get_test():
    url = "http://127.0.0.1:5000/timetable"
    response = requests.get(url)

    # Get the station data
    station_data = requests.get("http://127.0.0.1:5001/route/stations").json()
    # Create a mapping from station IDs to station names
    station_names = {station['id']: station['nameOfStation'] for station in station_data}

    return render_template('test.html', title='Test', data=response.json(), station_names=station_names)



from datetime import datetime

from flask import request

from flask import request

"""
@app.route('/search_ticket', methods=['POST','GET'])
def search_ticket():
    print('Inside search_ticket route')
    form = SearchTicketForm()
    if form.validate_on_submit():
        # Get the form data
        start_station = form.start_station.data
        print(f'Start station: {start_station}')
        end_station = form.end_station.data
        print(f'End station: {end_station}')
        date_string = form.date.data
        print(f'Date: {date_string}')

        # Convert the date string to a date object
        date = datetime.strptime(date_string, '%Y-%m-%d')

        # Get the station IDs
        answer = requests.get('http://127.0.0.1:5001/route/stations')
        stations = answer.json()
        print(f'Stations: {stations}')
        station_map = {station['nameOfStation']: station['id'] for station in stations}

        start_station_id = station_map.get(start_station)
        end_station_id = station_map.get(end_station)
        print(f'Start station ID: {start_station_id}')
        print(f'End station ID: {end_station_id}')

        if start_station_id is None or end_station_id is None:
            # One of the stations was not found in the station map
            return render_template('error.html', message='One or more stations not found')

        # Perform the search (replace this with your actual search logic)
        url = f"http://127.0.0.1:5000/timetable?start_station={start_station_id}&end_station={end_station_id}&date={date}"
        print(f'Request URL: {url}')
        answer = requests.get(url)

        if answer.status_code != 200:
            # The request to the timetable service failed
            print(f'Response status code: {answer.status_code}')
            return render_template('error.html', message='Failed to retrieve timetable data')

        search_results = answer.json()
        print(f'Search results: {search_results}')
        print('hi')

        if not search_results:
            # The search results are empty
            return render_template('error.html', message='No results found for the given criteria')

        print('hello')
        # Render a new template with the search results
        return render_template('search_results.html')

    return render_template('search_ticket.html', form=form)
"""

#search ticket, ist schon da, funktioniert!!!!!!
"""
@app.route('/search_ticket', methods=['POST','GET'])
def search_ticket():
    print('Inside search_ticket route')
    form = SearchTicketForm(request.form)
    if form.validate_on_submit():
        # Get the form data
        date_string = form.date.data
        print(f'Date: {date_string}')

        # Convert the date string to a date object
        date = datetime.strptime(date_string, '%Y-%m-%d')

        # Perform the search (replace this with your actual search logic)
        url = f"http://127.0.0.1:5000/timetable?date={date}"
        print(f'Request URL: {url}')
        answer = requests.get(url)

        if answer.status_code != 200:
            # The request to the timetable service failed
            print(f'Response status code: {answer.status_code}')
            return render_template('error.html', message='Failed to retrieve timetable data')

        search_results = answer.json()
        print(f'Search results: {search_results}')

        # Filter the results based on the date
        filtered_results = [result for result in search_results if result['datum'] == date_string]
        print(f'Filtered results: {filtered_results}')

        if not filtered_results:
            # The search results are empty
            return render_template('error.html', message='No results found for the given criteria')

        # Render a new template with the search results
        return render_template('search_results.html', results=filtered_results)

    # Render the search form when the form is not validated
    return render_template('search_ticket.html', form=form)

"""





@app.route('/search_ticket', methods=['POST','GET'])
def search_ticket():
    print('Inside search_ticket route')
    form = SearchTicketForm(request.form)
    if form.validate_on_submit():
        # Get the form data
        date_string = form.date.data
        start_station = form.start_station.data
        end_station = form.end_station.data
        print(f'Date: {date_string}, Start Station: {start_station}, End Station: {end_station}')

        # Convert the date string to a date object
        date = datetime.strptime(date_string, '%Y-%m-%d')

        # Get the station IDs
        answer = requests.get('http://127.0.0.1:5001/route/stations')
        stations = answer.json()
        station_map = {station['nameOfStation']: station['id'] for station in stations}
        start_station_id = station_map.get(start_station)
        end_station_id = station_map.get(end_station)

        # Perform the search
        url = f"http://127.0.0.1:5000/timetable?date={date}"
        print(f'Request URL: {url}')
        answer = requests.get(url)

        if answer.status_code != 200:
            # The request to the timetable service failed
            print(f'Response status code: {answer.status_code}')
            return render_template('error.html', message='Failed to retrieve timetable data')

        search_results = answer.json()
        print(f'Search results: {search_results}')

        # Filter the results based on the date and stations
        filtered_results = []
        for result in search_results:
            if result['datum'] == date_string and start_station_id in result['bahnhof_ids'] and end_station_id in result['bahnhof_ids']:
                # Get the index of the start station
                start_station_index = result['bahnhof_ids'].index(start_station_id)
                
                # Extract the departure time from the start station
                departure_time = result['zeiten'][start_station_index]
                
                # Add the departure time to the result
                result['departure_time'] = departure_time
                
                filtered_results.append(result)

        print(f'Filtered results: {filtered_results}')

        if not filtered_results:
            # The search results are empty
            return render_template('error.html', message='No results found for the given criteria')

        # Render a new template with the search results
        return render_template('search_results.html', results=filtered_results)

    # Render the search form when the form is not validated
    return render_template('search_ticket.html', form=form)


"""

@app.route('/search_ticket', methods=['POST','GET'])
def search_ticket():
    print('Inside search_ticket route')
    form = SearchTicketForm(request.form)
    if form.validate_on_submit():
        # Get the form data
        date_string = form.date.data
        start_station = form.start_station.data
        end_station = form.end_station.data
        print(f'Date: {date_string}, Start Station: {start_station}, End Station: {end_station}')

        # Convert the date string to a date object
        date = datetime.strptime(date_string, '%Y-%m-%d')

        # Get the station IDs
        answer = requests.get('http://127.0.0.1:5001/route/stations')
        stations = answer.json()
        station_map = {station['nameOfStation']: station['id'] for station in stations}
        start_station_id = station_map.get(start_station)
        end_station_id = station_map.get(end_station)

        # Perform the search
        url = f"http://127.0.0.1:5000/timetable?date={date}"
        print(f'Request URL: {url}')
        answer = requests.get(url)

        if answer.status_code != 200:
            # The request to the timetable service failed
            print(f'Response status code: {answer.status_code}')
            return render_template('error.html', message='Failed to retrieve timetable data')

        search_results = answer.json()
        print(f'Search results: {search_results}')

        # Filter the results based on the date and stations
        filtered_results = []
        for result in search_results:
            if result['datum'] == date_string and start_station_id in result['bahnhof_ids'] and end_station_id in result['bahnhof_ids']:
                # Get the index of the start station and end station
                start_station_index = result['bahnhof_ids'].index(start_station_id)
                end_station_index = result['bahnhof_ids'].index(end_station_id)

                # Extract the departure time from the start station
                departure_time = result['zeiten'][start_station_index]

                # Add the departure time to the result
                result['departure_time'] = departure_time

                # Calculate the price from the start station to the end station
                if start_station_index < end_station_index:
                    price = sum(result['preise'][start_station_index:end_station_index])
                else:
                    price = sum(result['preise'][end_station_index:start_station_index])

                # Add the price to the result
                result['price'] = price

                filtered_results.append(result)

        print(f'Filtered results: {filtered_results}')

        if not filtered_results:
            # The search results are empty
            return render_template('error.html', message='No results found for the given criteria')

        # Render a new template with the search results
        return render_template('search_results.html', results=filtered_results)

    # Render the search form when the form is not validated
    return render_template('search_ticket.html', form=form)

    """

@app.route('/buy_ticket')
def buy_ticket():
    zug_id = request.args.get('zug_id')
    # Handle the ticket buying process here
    return render_template('confirmation.html', zug_id=zug_id)

#real data - try !!!!!!!pip install wtformspip install wtformspip install wtforms
def fetch_data_from_url():
    url = "http://127.0.0.1:5000/timetable"
    response = requests.get(url)
    #print(response.json().get('preise'))
    #json and python 

    if response.status_code != 200:
        print('Failed to fetch data: HTTP ' + str(response.status_code))
        return

    data = json.loads(response.text)
    return data

# Search for journeys on a specific date
def search_journeys_by_date(data, date):
    return [journey for journey in data if journey['datum'] == date]

# Use the functions
data = fetch_data_from_url()
if data is not None:
    print("Fetched data successfully")
    journeys = search_journeys_by_date(data, "2023-12-28")
    print(f"Found {len(journeys)} journeys on 2023-12-28")
else:
    print("Failed to fetch data")





#a dictionary mapping station IDs to station names
station_ids_to_names = {12: "Station1", 11: "Station2", 10: "Station3", 9: "Station4", 4: "Station5", 5: "Station6", 6: "Station7", 8: "Station8", 7: "Station9", 14: "Station10", 13: "Station11"}


#a function to search for journeys between two stations at a specific time
def search_journeys_by_stations_and_time(data, start_station, end_station, time):
    return [journey for journey in data if start_station in journey['bahnhof_ids'] and end_station in journey['bahnhof_ids'] and journey['zeit'] <= time and journey['endzeit'] >= time]

#a function to calculate the total price for a journey between two stations
def calculate_price(journey, start_station, end_station):
    start_index = journey['bahnhof_ids'].index(start_station)
    end_index = journey['bahnhof_ids'].index(end_station)
    return sum(journey['preise'][start_index:end_index])


"""
@app.route('/search', methods=['GET'])
def search_journey():
    start_station = request.args.get('start_station')
    end_station = request.args.get('end_station')
    time = request.args.get('time')
    print(f'die Daten {time}, {start_station} und{end_station} stimmen noch') #damit siehst du wie die daten daherkommen aus dem request

    # Filter journeys and stations based on the query parameters
    filtered_journeys = []
    for journey in data['journeys']:
        print('hier kommt man noch rein 1')
        stations_in_journey = [station for station in data['stations'] if station['journey_id'] == journey['id']]
        print(f'hier kommt man auch noch rein  mit {stations_in_journey}')
        if any(station['name'] == start_station and station['departure_time'] <= time for station in stations_in_journey) and \
           any(station['name'] == end_station and station['arrival_time'] >= time for station in stations_in_journey):
            print('hier kommt man noch rein 2')
            filtered_journeys.append(journey)
            print('hier kommt man noch rein 3')

    return jsonify(filtered_journeys)

"""    
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
    flash('Trains fetched and saved successfully.')



from flask import request
import requests
from datetime import datetime
from flask import request, abort
import requests
from datetime import datetime
import json

def get_timetable():
    print("get_timetable")
    response = requests.get("http://127.0.0.1:5000/timetable")
    if response.status_code == 200:
        return response.json()
    else:
        return []
    
"""
@app.route('/fetch_schedule', methods=['POST'])
def fetch_schedule():
    url = request.data.decode('utf-8')  # Get the URL of the API from the request body
    data = get_timetable()
    print(data)

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
"""



# Routen zum Importieren der Daten Ende
#get oder post??? 
@app.route('/fetch_stations', methods=['POST'])
def fetch_stations():
    fetch_and_save_stations()
    fetch_and_save_sections()
    fetch_and_save_lines()
    fetch_and_save_events()
    fetch_and_save_trains()
    #fetch_schedule()
    return redirect(url_for('index'))


#ticket, wer, was, wohin - nur requests zu schicken, application design, nicht mehr änderbar, arbeiten, was sie schicken, nicht kompatibel, dummy daten


#vorher auskommentiert
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






if __name__ == '__main__':
    print('Starting application with app.run()')
    app.run(port=5003, debug=True)



#get_fahrtdurchfuehrungen()  # Call the function here


#neu suchen


"""
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
    """


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



###new start

"""
def populate_db():
    # Your test data
    data = {
      "journeys": [
        {
          "id": 1,
          "start_station_id": 1,
          "end_station_id": 2,
          "date": "2022-12-01",
          "available_seats": 50,
          "price": 25.50
        },
        {
          "id": 2,
          "start_station_id": 3,
          "end_station_id": 4,
          "date": "2022-12-02",
          "available_seats": 60,
          "price": 30.00
        }
      ],
      "stations": [
        {
          "id": 1,
          "name": "Station A",
          "arrival_time": "2022-12-01T08:00:00",
          "departure_time": "2022-12-01T08:30:00",
          "journey_id": 1
        },
        {
          "id": 2,
          "name": "Station B",
          "arrival_time": "2022-12-01T10:00:00",
          "departure_time": "2022-12-01T10:30:00",
          "journey_id": 1
        },
        {
          "id": 3,
          "name": "Station C",
          "arrival_time": "2022-12-02T08:00:00",
          "departure_time": "2022-12-02T08:30:00",
          "journey_id": 2
        },
        {
          "id": 4,
          "name": "Station D",
          "arrival_time": "2022-12-02T10:00:00",
          "departure_time": "2022-12-02T10:30:00",
          "journey_id": 2
        }
      ]
    }

    # Populate the database
       # Populate the database
    for journey_data in data['journeys']:
        journey_data['date'] = datetime.strptime(journey_data['date'], '%Y-%m-%d').date()
        journey = Journey(**journey_data)
        db.session.add(journey)
        
    for station_data in data['stations']:
        station_data['arrival_time'] = datetime.strptime(station_data['arrival_time'], '%Y-%m-%dT%H:%M:%S')
        station_data['departure_time'] = datetime.strptime(station_data['departure_time'], '%Y-%m-%dT%H:%M:%S')
        station = Trainstation(**station_data)
        db.session.add(station)
    db.session.commit()

@app.route('/populate_db', methods=['POST'])
def route_populate_db():
    populate_db()
    return "Database populated successfully", 200
    """

#new new new 

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)



