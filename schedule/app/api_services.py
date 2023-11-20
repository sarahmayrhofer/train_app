import requests
from datetime import datetime, timedelta

def get_lines():
    response = requests.get("http://127.0.0.1:5001/route/lines")
    if response.status_code == 200:
        return response.json()
    else:
        return []

def berechne_preise_und_bahnhof_ids(line):
    preise = []
    bahnhof_ids = [line['startStationId']]
    for section in line['sections']:
        preis = section['distance'] * 1.12
        preise.append(preis)
        bahnhof_ids.append(section['endStationId'])
    return preise, bahnhof_ids

def berechne_zeiten(line, startzeit_string):
    # Konvertieren Sie den Startzeit-String in ein datetime-Objekt, das nur die Zeit beinhaltet
    startzeit = datetime.strptime(startzeit_string, '%H:%M')

    zeiten = [startzeit]
    for section in line['sections']:
        # Berechnen der Zeitdauer für die Sektion in Stunden
        dauer_in_sekunden = section['distance'] / section['maxSpeed'] * 3600 # Stunden in Sekunden umrechnen

        # Hinzufügen der Dauer zur letzten Zeit
        neue_zeit = zeiten[-1] + timedelta(seconds=dauer_in_sekunden)
        zeiten.append(neue_zeit)

    # Konvertieren Sie die datetime-Objekte zurück in Strings, wenn nötig
    return [zeit.strftime('%H:%M:%S') for zeit in zeiten]

def hole_line(line_id):
    try:
        response = requests.get("http://127.0.0.1:5001/route/lines")
        if response.status_code == 200:
            lines = response.json()
            # Wählen Sie die Linie mit der passenden ID
            for line in lines:
                if line["id"] == line_id:
                    return line
            # Keine Linie mit der gegebenen ID gefunden
            return None
        else:
            # Fehler oder keine Daten gefunden
            return None
    except requests.RequestException as e:
        # Fehlerbehandlung, z.B. Logging des Fehlers
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None