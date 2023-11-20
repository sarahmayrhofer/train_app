from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from .models import Fahrtdurchführung, Train
from app.db import db
from datetime import datetime
from .api_services import get_stations

main = Blueprint('main', __name__)

def register_routes(app):
    app.register_blueprint(main)

@main.route('/')
def startseite():
    return render_template('startseite.html') 

@main.route('/fahrtdurchfuehrungen/')
def fahrtdurchfuehrungen():
    alle_fahrtdurchfuehrungen = Fahrtdurchführung.query.all()
    return render_template('fahrtdurchfuehrungen.html', fahrtdurchfuehrungen=alle_fahrtdurchfuehrungen)

@main.route('/neue_fahrtdurchfuehrung', methods=['GET', 'POST'])
def neue_fahrtdurchfuehrung():
    if request.method == 'POST':
        daten = request.form.getlist('daten[]') 
        zeiten = request.form.getlist('zeiten[]')
        start_station_id = request.form.get('station_id')
        zug_id = request.form.get('zug_id') 
        mitarbeiter_ids = request.form.get('mitarbeiter_ids')

        for datum_string in daten:
            for zeit_string in zeiten:
                datum = datetime.strptime(datum_string, '%Y-%m-%d').date()
                zeit = datetime.strptime(zeit_string, '%H:%M').time()
                neue_fahrt = Fahrtdurchführung(datum=datum, zeit=zeit, zug_id=zug_id, start_station=start_station_id, mitarbeiter_ids=mitarbeiter_ids)
                db.session.add(neue_fahrt)
        
        db.session.commit()

        return redirect(url_for('main.fahrtdurchfuehrungen'))

    # Hier wird das Formular für eine GET-Anfrage gerendert
    zuege = Train.query.all()  # Liste der Züge abfragen
    stations = get_stations()
    return render_template('neue_fahrtdurchfuehrung.html', zuege=zuege, stations=stations)  # Liste an die Vorlage übergeben

@main.route('/loesche_fahrtdurchfuehrung/<int:id>', methods=['POST'])
def loesche_fahrtdurchfuehrung(id):
    fahrt = Fahrtdurchführung.query.get_or_404(id)
    db.session.delete(fahrt)
    db.session.commit()
    return redirect(url_for('main.fahrtdurchfuehrungen'))