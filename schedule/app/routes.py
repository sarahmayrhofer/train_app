from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for, jsonify
from .models import Fahrtdurchführung
from app.db import db
from datetime import datetime
from .api_services import *
import json

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

    # Hier wird das Formular für eine GET-Anfrage gerendert
    zuege = get_trains()  # Liste der Züge abfragen
    lines = get_lines()
    return render_template('neue_fahrtdurchfuehrung.html', zuege=zuege, lines=lines)  # Liste an die Vorlage übergeben

@main.route('/loesche_fahrtdurchfuehrung/<int:id>', methods=['POST'])
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