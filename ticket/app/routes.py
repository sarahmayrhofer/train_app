
from datetime import datetime
import random
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
from app.models import Station
from flask import redirect, url_for

import http.client
import json
from flask import flash
from app.models import Station
import requests
import socket

from flask import request, jsonify
from . import app
from flask import request

#new
from app.models import Journey, Trainstation

from .forms import SearchTicketForm
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from app.models import Ticket

from datetime import datetime
from flask import Flask, render_template
from flask import flash, redirect, url_for
from app.models import Timetable

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


#Login

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

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}


#Logout 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



from datetime import datetime
from flask import request
import requests


#traindata hilfsfunktion
def get_train_data():
    response = requests.get('http://127.0.0.1:5002/fleet/trains')
    if response.status_code == 200:
        return response.json()
    else:
        return None


#hilfsmethode für search_ticket
    
def get_total_seats(train_data, train_id):
    # First, try to get the available seats from the Timetable model
    timetable = Timetable.query.filter_by(zug_id=train_id).first()
    if timetable is not None:
        return timetable.available_seats

    # If the timetable does not exist, calculate the total seats from the train data
    total_seats = 0
    for train in train_data:
        print(f"Checking train with id {train['id']} against train_id {train_id}")
        if train['id'] == train_id:
            for wagon in train['wagons']:
                if 'number_of_seats' in wagon:
                    total_seats += wagon['number_of_seats']
    return total_seats




@app.route('/search_ticket', methods=['POST','GET'])
def search_ticket():
    print('Inside search_ticket route')
    form = SearchTicketForm(request.form)
    if form.validate_on_submit():
        # Get the form data
        date_string = form.date.data if form.date.data else None
        start_station = form.start_station.data if form.start_station.data else None
        end_station = form.end_station.data if form.end_station.data else None
        print(f'Date: {date_string}, Start Station: {start_station}, End Station: {end_station}')

        # Convert the date string to a date object if date_string is not None
        date = datetime.strptime(date_string, '%Y-%m-%d') if date_string else None

        # Get the station IDs
        answer = requests.get('http://127.0.0.1:5001/route/stations')
        stations = answer.json()
        station_map = {station['nameOfStation']: station['id'] for station in stations}
        start_station_id = station_map.get(start_station) if start_station else None
        end_station_id = station_map.get(end_station) if end_station else None

        # Perform the search
        url = f"http://127.0.0.1:5000/timetable"
        if date:
            url += f"?date={date}"
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
            if (not date_string or result['datum'] == date_string) and \
               (not start_station_id or start_station_id in result['bahnhof_ids']) and \
               (not end_station_id or end_station_id in result['bahnhof_ids']):
                # Get the index of the start station and end station if they exist
                start_station_index = result['bahnhof_ids'].index(start_station_id) if start_station_id else None
                end_station_index = result['bahnhof_ids'].index(end_station_id) if end_station_id else None

                # Extract the departure time from the start station if it exists
                departure_time = result['zeiten'][start_station_index] if start_station_index else None

                # Add the departure time to the result if it exists
                if departure_time:
                    result['departure_time'] = departure_time

                # Add the start station and end station to the result if they exist
                if start_station:
                    result['start_station'] = start_station
                if end_station:
                    result['end_station'] = end_station

                # Calculate the price from the start station to the end station if they exist
                if start_station_index is not None and end_station_index is not None:
                    if start_station_index < end_station_index:
                        price = sum(result['preise'][start_station_index:end_station_index])
                    else:
                        price = sum(result['preise'][end_station_index:start_station_index])

                    #old version without date
                    """
                    # Fetch all Sale objects for the original_line and sort them by discount in descending order
                    sales = Sale.query.filter_by(lineForTheSale=result['original_line']).order_by(Sale.discount.desc()).all()

                    # Apply the highest discount if any Sale objects exist for the line
                    if sales:
                        price = price * (1 - sales[0].discount / 100)
                    
                    # Add the price to the result
                    result['price'] = price
                    """

                    # Assume `search_date` is the date you're searching for, make sure it's a date object
                    search_date = datetime.strptime(date_string, '%Y-%m-%d').date() if date_string else None

                    # Fetch all Sale objects for the original_line that are active on the search date
                    # and sort them by discount in descending order
                    sales = Sale.query.filter(
                        Sale.lineForTheSale == result['original_line'],
                        Sale.start_date <= search_date,
                        Sale.end_date >= search_date
                    ).order_by(Sale.discount.desc()).all()

                    # Apply the highest discount if any Sale objects exist for the line
                    if sales:
                        price = price * (1 - sales[0].discount / 100)
                    
                    # Add the price to the result
                    result['price'] = price

                # Get the total number of seats for the train
                # Get the total number of seats for the train
                if 'zug_id' in result:
                    print(f"Getting total seats for train_id {result['zug_id']}")
                    train_data = get_train_data()
                    total_seats = get_total_seats(train_data, result['zug_id'])
                    result['total_seats'] = total_seats

                    if total_seats > 0:
                        price /= total_seats
                        result['price'] = price
            
                    # Save the timetable data to the database
                    timetable = Timetable.query.get(result['id'])
                    if timetable is None:
                        timetable = Timetable(id=result['id'], zug_id=result['zug_id'], datum=date, available_seats=total_seats)
                        db.session.add(timetable)
                    else:
                        timetable.zug_id = result['zug_id']
                        timetable.datum = date
                        timetable.available_seats = total_seats
                    db.session.commit()
                else:
                    print(f"train_id not found in result: {result}")
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


#ticket kaufen
@app.route('/buy_ticket')
def buy_ticket():
    with_seat = request.args.get('with_seat')
    zug_id = request.args.get('zug_id')
    date = request.args.get('date')
    start_station = request.args.get('start_station')
    end_station = request.args.get('end_station')
    price = request.args.get('price')

    # Convert the date string to a date object
    date = datetime.strptime(date, '%Y-%m-%d')

    # Check if the date is in the future
    if date < datetime.utcnow():
        flash('Cannot buy a ticket for a past date.')
        error_message = "An error occurred, the date has already passed."
        return render_template('fehler_date.html', error_message=error_message)

    seat_number = None

    if with_seat:
        # Fetch the timetable for the train
        timetable = Timetable.query.filter_by(zug_id=zug_id).first()

        if timetable is not None:
            # Get the number of available seats
            available_seats = timetable.available_seats

            # Reserve a seat if available
            if available_seats > 0:
                seat_number = available_seats - 1

                # Update the number of available seats
                timetable.available_seats -= 1
                db.session.commit()
            else:
                flash('No seats available.')
                return redirect(url_for('search_ticket'))  # replace with the actual route name
        else:
            flash('Timetable not found.')
            return redirect(url_for('search_ticket'))  # replace with the actual route name

    # Handle the ticket buying process here
    seat_state = False
    if with_seat:
        seat_state = True
    ticket = Ticket(user_id=current_user.id, zug_id=zug_id, date=date, start_station=start_station, end_station=end_station, price=price, seat_reserved=seat_state, seat_number=seat_number, status='active')
    db.session.add(ticket)
    db.session.commit()

    return render_template('confirmation.html', zug_id=zug_id)
  

@app.route('/my_tickets')
@login_required
def my_tickets():
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('my_tickets.html', tickets=tickets)

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket and ticket.user_id == current_user.id:
        if ticket.status == 'passed':
            flash('Cannot delete a ticket with status passed.')
        else:
            # Always increase the available seats for the train when a ticket is deleted
            timetable = Timetable.query.filter_by(zug_id=ticket.zug_id).first()
            if timetable:
                timetable.available_seats += 1
                db.session.commit()

            ticket.status = 'deleted'
            db.session.commit()
            flash('Ticket marked as deleted.')
    else:
        flash('Ticket not found.')
    return redirect(url_for('my_tickets'))



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


#Sales SECTION
@app.route('/create_sale', methods=['GET', 'POST'])
def create_sale():
    form = SaleForm()
    form.line.choices = [('all', 'All Lines')] + [(line.id, line.nameOfLine) for line in Line.query.order_by('nameOfLine')]
    if form.validate_on_submit():
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        # Check if the discount should be applied to all lines
        if form.line.data == 'all':
            lines = Line.query.all()
            for line in lines:
                sale = Sale(discount=form.discount.data, lineForTheSale=line.id, all_lines=True, start_date=start_date, end_date=end_date)  # Set start_date and end_date
                db.session.add(sale)
        else:
            sale = Sale(discount=form.discount.data, lineForTheSale=form.line.data, all_lines=False, start_date=start_date, end_date=end_date)  # Set start_date and end_date
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
        sale.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        sale.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('sales'))

    elif request.method == 'GET':
        form.discount.data = sale.discount
        form.line.data = sale.lineForTheSale
        form.start_date.data = sale.start_date.strftime('%Y-%m-%d')
        form.end_date.data = sale.end_date.strftime('%Y-%m-%d')

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
        train.total_number_of_seats = 0

        for wagon_data in train_data['wagons']:
            wagon = Wagon.query.get(wagon_data['id'])
            print(wagon)
            if wagon is None:
                if wagon_data['wagon_type'] == 'locomotive':
                    wagon = Locomotive(id=wagon_data['id'])
                else:
                    wagon = NormalWagon(id=wagon_data['id'], number_of_seats=wagon_data.get('number_of_seats', 0))
                db.session.add(wagon)
            wagon.track_width = wagon_data['track_width']
            wagon.train = train
            if wagon.number_of_seats is not None:
                train.total_number_of_seats += wagon.number_of_seats

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

#wird nicht verwendet
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



