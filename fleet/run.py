from flask import Flask

app = Flask(__name__)


# Index Page
@app.route('/')
def index():
    return "Welcome to the Fleet Information System"


# Trains Overview
@app.route('/trains/')
def trains_overview():
    return "Trains Overview Page"


# Train by ID
@app.route('/trains/<int:train_id>')
def train_by_id(train_id):
    return f"Train with ID {train_id}"


# Users Page
@app.route('/users')
def users():
    return "Users Page"


# User by ID
@app.route('/users/<int:user_id>')
def user_by_id(user_id):
    return f"User with ID {user_id}"


# Maintenance Overview
@app.route('/maintenances')
def maintenance_overview():
    return "Maintenance Overview Page"


# Maintenance by ID
@app.route('/maintenance/<int:maintenance_id>')
def maintenance_by_id(maintenance_id):
    return f"Maintenance with ID {maintenance_id}"


if __name__ == '__main__':
    app.run(debug=True)
