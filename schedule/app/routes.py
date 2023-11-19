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
    return render_template('startseite.html')  # Stellen Sie sicher, dass Sie eine entsprechende Vorlage haben

@main.route('/fahrtdurchfuehrungen/')
def fahrtdurchfuehrungen():
    alle_fahrtdurchfuehrungen = Fahrtdurchführung.query.all()
    return render_template('fahrtdurchfuehrungen.html', fahrtdurchfuehrungen=alle_fahrtdurchfuehrungen)

@main.route('/neue_fahrtdurchfuehrung', methods=['GET', 'POST'])
def neue_fahrtdurchfuehrung():
    if request.method == 'POST':
        datum_string = request.form['datum']  # Datum als String
        datum = datetime.strptime(datum_string, '%Y-%m-%d').date()  # Konvertierung in ein date-Objekt
        start_station_id = request.form.get('station_id')
        zug_id = request.form.get('zug_id')  # Hier sollten Sie sicherstellen, dass Sie eine gültige Zug-ID erhalten

        neue_fahrt = Fahrtdurchführung(datum=datum, zug_id=zug_id, start_station=start_station_id)
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