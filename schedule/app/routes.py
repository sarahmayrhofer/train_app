from flask import Blueprint
from flask import flash
from flask import render_template
from flask import request, redirect, url_for, jsonify
from .models import Fahrtdurchführung, Streckenhalteplan, User
from app.db import db
from datetime import datetime
from .api_services import *
import json
from .forms import LoginForm, NewUserForm, RegistrationForm
from flask_login import login_user, current_user, login_required
from werkzeug.urls import url_parse
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Diese Seite ist nur für Administratoren zugänglich.", "warning")
            return redirect(url_for('main.index'))  # Oder eine andere geeignete Route
        return f(*args, **kwargs)
    return decorated_function


main = Blueprint('main', __name__)

def register_routes(app):
    app.register_blueprint(main)

@main.route('/')
def startseite():
    return redirect(url_for('main.login'))

@main.route('/index')
def index():
    return render_template('index.html', page_name='Übersicht', user=current_user)

@main.route('/fahrtdurchfuehrungen/')
@login_required
def fahrtdurchfuehrungen():
    alle_fahrtdurchfuehrungen = Fahrtdurchführung.query.order_by(Fahrtdurchführung.datum, Fahrtdurchführung.zeit).all()
    return render_template('fahrtdurchfuehrungen.html', page_name='Fahrtdurchführungen', user=current_user, fahrtdurchfuehrungen=alle_fahrtdurchfuehrungen)

@main.route('/neue_fahrtdurchfuehrung', methods=['GET', 'POST'])
@login_required
@admin_required
def neue_fahrtdurchfuehrung():
    #GET
    alle_mitarbeiter = User.query.all()
    zuege = get_trains()  # Liste der Züge abfragen
    streckenhalteplaene = Streckenhalteplan.query.all()
    lines = get_prepared_lines(streckenhalteplaene)

    #POST
    if request.method == 'POST':
        daten = request.form.getlist('daten[]') 
        zeiten = request.form.getlist('zeiten[]')
        line_id = request.form.get('line_id')
        zug_id = request.form.get('zug_id') 
        mitarbeiter_ids = request.form.get('mitarbeiter_ids')
        line = hole_line_prepared(int(line_id), lines) # Funktion, die die Linieninformation abruft
        percent_profit = request.form.get('percent_profit', type=int) or 0

        for datum_string in daten:
            for zeit_string in zeiten:
                preise, bahnhof_ids = berechne_preise_und_bahnhof_ids(line, percent_profit)
                arr_zeiten = berechne_zeiten(line, zeit_string)

                datum = datetime.strptime(datum_string, '%Y-%m-%d').date()
                zeit = datetime.strptime(zeit_string, '%H:%M').time()
                neue_fahrt = Fahrtdurchführung(datum=datum, zeit=zeit, endzeit= (datetime.strptime(arr_zeiten[-1], '%H:%M:%S')).time(), zug_id=zug_id, line=line_id, mitarbeiter_ids=mitarbeiter_ids, preise=str(preise), bahnhof_ids=str(bahnhof_ids), zeiten=str(arr_zeiten))
                db.session.add(neue_fahrt)
        
        db.session.commit()

        return redirect(url_for('main.fahrtdurchfuehrungen'))

    #GET-Anfrage gerendert
    return render_template('neue_fahrtdurchfuehrung.html', page_name='Fahrtdurchführung anlegen', user=current_user, zuege=zuege, lines=lines, alle_mitarbeiter=alle_mitarbeiter)  # Liste an die Vorlage übergeben

@main.route('/loesche_fahrtdurchfuehrung/<int:id>', methods=['POST'])
@login_required
@admin_required
def loesche_fahrtdurchfuehrung(id):
    fahrt = Fahrtdurchführung.query.get_or_404(id)
    db.session.delete(fahrt)
    db.session.commit()
    return redirect(url_for('main.fahrtdurchfuehrungen'))

@main.route('/timetable', methods=['GET'])
def api_fahrtdurchfuehrungen():
    alle_fahrtdurchfuehrungen = Fahrtdurchführung.query.all()
    fahrtdurchfuehrungen_liste = []

    for fahrt in alle_fahrtdurchfuehrungen:
        fahrt_dict = {
            'id': fahrt.id,
            'datum': fahrt.datum.isoformat(),
            'zeit': fahrt.zeit.isoformat() if fahrt.zeit else None,
            'endzeit': fahrt.endzeit.isoformat() if fahrt.endzeit else None,
            'zug_id': fahrt.zug_id,
            'line': fahrt.line,
            'mitarbeiter_ids': [int(id.strip()) for id in fahrt.mitarbeiter_ids.split(',')] if fahrt.mitarbeiter_ids else [],
            'preise': [float(preis.strip()) for preis in fahrt.preise[1:-1].split(',')] if fahrt.preise else [],
            'bahnhof_ids': [int(id.strip()) for id in fahrt.bahnhof_ids[1:-1].split(',')] if fahrt.bahnhof_ids else [],
            'zeiten': [zeit.strip() for zeit in fahrt.zeiten[1:-1].split(',')] if fahrt.zeiten else []
        }
        fahrtdurchfuehrungen_liste.append(fahrt_dict)

    return jsonify(fahrtdurchfuehrungen_liste)

#Route zur Übersicht für Streckenhaltepläne
@main.route('/streckenhalteplaene')
@login_required
def streckenhalteplaene():
    alle_streckenhalteplaene = Streckenhalteplan.query.all()
    return render_template('streckenhalteplaene.html', page_name='Streckenhaltepläne', user=current_user, streckenhalteplaene=alle_streckenhalteplaene)

# Route für die erstellung eines Streckenhalteplans
@main.route('/streckenhalteplan/')
@login_required
@admin_required
def streckenhalteplan():
    lines = get_lines()
    all_stations = get_all_stations() 
    return render_template('streckenhalteplan.html', page_name='Streckenhalteplan anlegen', user=current_user, lines=lines, all_stations=all_stations)

@main.route('/save_streckenhalteplan', methods=['POST'])
@login_required
@admin_required
def save_streckenhalteplan():
    data = request.json
    stations_status = data['stations_status']
    line_data = hole_line(int(data['line_id']))  # Holt die vollständige Linieninformation
    if not line_data:
        return jsonify({"error": "Linie nicht gefunden"}), 404

    # Erstellen eines neuen Streckenhalteplan-Objekts mit den angepassten Daten
    streckenhalteplan_id = create_streckenhalteplan(line_data, data['name'], stations_status)

    return redirect(url_for('main.streckenhalteplaene'))

@main.route('/loesche_streckenhalteplan/<int:id>', methods=['POST'])
@login_required
@admin_required
def loesche_streckenhalteplan(id):
    plan = Streckenhalteplan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    return redirect(url_for('main.streckenhalteplaene'))

#USER
# Users Page
@main.route('/users/')
@main.route('/users')
@login_required
def users():
    users = User.query.all()

    return render_template('users.html', page_name='Userverwaltung', user=current_user, users=users)


@main.route('/newUser', methods=['GET', 'POST'])
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

    return render_template('new_user.html', page_name='Mitarbeiter anlegen', user=current_user, form=form)


# User by ID
@main.route('/users/<int:user_id>')
def user_by_id(user_id):
    return f"User with ID {user_id}"

# Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', page_name='Login', user=current_user, title='Sign In', form=form)


# Register - just user - no admin
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))

    return render_template('register.html', page_name='Registrierung', user=current_user, title='Register', form=form)
