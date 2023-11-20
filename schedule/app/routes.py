from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for, jsonify
from .models import Fahrtdurchführung, Train
from app.db import db
from datetime import datetime
from .api_services import *

main = Blueprint('main', __name__)

def register_routes(app):
    app.register_blueprint(main)

@main.route('/')
def startseite():
    return render_template('startseite.html') 

@main.route('/fahrtdurchfuehrungen/')
def fahrtdurchfuehrungen():
    alle_fahrtdurchfuehrungen = Fahrtdurchführung.query.order_by(Fahrtdurchführung.datum, Fahrtdurchführung.zeit).all()
    return render_template('fahrtdurchfuehrungen.html', fahrtdurchfuehrungen=alle_fahrtdurchfuehrungen)

@main.route('/neue_fahrtdurchfuehrung', methods=['GET', 'POST'])
def neue_fahrtdurchfuehrung():
    if request.method == 'POST':
        daten = request.form.getlist('daten[]') 
        zeiten = request.form.getlist('zeiten[]')
        line_id = request.form.get('line_id')
        zug_id = request.form.get('zug_id') 
        mitarbeiter_ids = request.form.get('mitarbeiter_ids')
        line = hole_line(int(line_id))  # Funktion, die die Linieninformation abruft

        for datum_string in daten:
            for zeit_string in zeiten:
                preise, bahnhof_ids = berechne_preise_und_bahnhof_ids(line)
                arr_zeiten = berechne_zeiten(line, zeit_string)

                datum = datetime.strptime(datum_string, '%Y-%m-%d').date()
                zeit = datetime.strptime(zeit_string, '%H:%M').time()
                neue_fahrt = Fahrtdurchführung(datum=datum, zeit=zeit, endzeit= (datetime.strptime(arr_zeiten[-1], '%H:%M:%S')).time(), zug_id=zug_id, line=line_id, mitarbeiter_ids=mitarbeiter_ids, preise=str(preise), bahnhof_ids=str(bahnhof_ids), zeiten=str(arr_zeiten))
                db.session.add(neue_fahrt)
        
        db.session.commit()

        return redirect(url_for('main.fahrtdurchfuehrungen'))

    # Hier wird das Formular für eine GET-Anfrage gerendert
    zuege = Train.query.all()  # Liste der Züge abfragen
    lines = get_lines()
    return render_template('neue_fahrtdurchfuehrung.html', zuege=zuege, lines=lines)  # Liste an die Vorlage übergeben

@main.route('/loesche_fahrtdurchfuehrung/<int:id>', methods=['POST'])
def loesche_fahrtdurchfuehrung(id):
    fahrt = Fahrtdurchführung.query.get_or_404(id)
    db.session.delete(fahrt)
    db.session.commit()
    return redirect(url_for('main.fahrtdurchfuehrungen'))

@main.route('/check_availability')
def check_availability():
    zug_id = request.args.get('zug_id')
    datum = request.args.get('datum')
    zeit = request.args.get('zeit')
    line_id = request.args.get('line_id')

    # Konvertieren Sie Datum und Zeit in ein DateTime-Objekt
    startzeit_obj = datetime.strptime(f'{datum} {zeit}', '%Y-%m-%d %H:%M')

    # Holen Sie die Linieninformationen, um die Gesamtdauer zu berechnen
    line = hole_line(int(line_id))
    if line is None:
        return jsonify({'error': 'Linie nicht gefunden'}), 400

    gesamtdauer = sum([section['distance'] / section['maxSpeed'] for section in line['sections']])
    endzeit_obj = startzeit_obj + timedelta(hours=gesamtdauer)

    # Überprüfen Sie, ob der Zug zu diesem Zeitraum belegt ist
    konflikt = Fahrtdurchführung.query.filter_by(zug_id=zug_id).filter(
        (Fahrtdurchführung.datum == datum) &
        ((Fahrtdurchführung.zeit <= startzeit_obj) & (Fahrtdurchführung.endzeit >= startzeit_obj) |
         (Fahrtdurchführung.zeit <= endzeit_obj) & (Fahrtdurchführung.endzeit >= endzeit_obj))
    ).first() is not None

    return jsonify({'belegt': konflikt})