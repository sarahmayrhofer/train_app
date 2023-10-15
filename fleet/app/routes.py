from flask import Blueprint
from flask import render_template

main = Blueprint('main', __name__)


# Index Page
@main.route('/')
def index():
    user = {'username': 'Tobias Schwap'}
    return render_template('index.html', page_name='Übersicht', user=user)


# Trains Overview
@main.route('/trains/')
@main.route('/trains')
def trains_overview():
    return "Trains Overview Page"


# Train by ID
@main.route('/trains/<int:train_id>')
def train_by_id(train_id):
    return f"Train with ID {train_id}"


# Users Page
@main.route('/users/')
@main.route('/users')
def users():
    return "Users Page"


# User by ID
@main.route('/users/<int:user_id>')
def user_by_id(user_id):
    return f"User with ID {user_id}"


# Maintenance Overview
@main.route('/maintenances/')
@main.route('/maintenances')
def maintenance_overview():
    return "Maintenance Overview Page"


# Maintenance by ID
@main.route('/maintenances/<int:maintenance_id>')
def maintenance_by_id(maintenance_id):
    return f"Maintenance with ID {maintenance_id}"
