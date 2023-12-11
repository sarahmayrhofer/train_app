
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, SaleForm
from app.models import Sale, User, Line
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
from bs4 import BeautifulSoup

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

@app.route('/fetch_stations', methods=['POST'])
def fetch_stations():
    fetch_and_save_stations()
    return redirect(url_for('index'))







# Routen zum Importieren der Daten Ende
#neue route shedule

def get_fahrtdurchfuehrungen():
    response = requests.get("http://127.0.0.1:5000/fahrtdurchfuehrungen/")
    soup = BeautifulSoup(response.text, 'html.parser')

    # Now you can use the soup object to parse the HTML
    for item in soup.find_all('tr'):
        print(item)


    #print(response.text)

    # Only parse the response as JSON if it's not empty
    #if response.text:
     #   data = response.json()
        
        # Now you can use the data
      #  for item in data:
       #     print(item)
    else:
        print("No data received from the server.")
   

get_fahrtdurchfuehrungen()  # Call the function here


if __name__ == '__main__':
    print('Starting application with app.run()')
    app.run(port=5003)