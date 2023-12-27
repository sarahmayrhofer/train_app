import requests
from datetime import datetime, timedelta
from app.models import Streckenhalteplan, Section
from app.db import db

def get_lines():
    response = requests.get("http://127.0.0.1:5001/route/lines")
    if response.status_code == 200:
        return response.json()
    else:
        return []

def get_prepared_lines(streckenhalteplaene):
    # Formatieren Sie die Streckenhaltepläne in das benötigte Format
    lines = []
    for plan in streckenhalteplaene:
        line = {
            'id': plan.id,
            'nameOfLine': plan.name,
            'startStationId': plan.start_station_id,
            'endStationId': plan.end_station_id,
            'original_line_id': plan.original_line_id,
            'travel_duration': plan.travel_duration,
            'sections': format_sections(plan.sections)
        }
        lines.append(line)
    return lines

def format_sections(sections):
    # Formatieren Sie die Sektionen entsprechend
    formatted_sections = []
    for section in sections:
        formatted_section = {
            'id': section.id,
            'startStationId': section.startStation,
            'endStationId': section.endStation,
            'fee': section.fee, 
            'distance': section.distance,
            'maxSpeed': section.maxSpeed,
            'trackWidth': section.trackWidth
        }
        formatted_sections.append(formatted_section)
    return formatted_sections

def get_all_stations():
    response = requests.get("http://127.0.0.1:5001/route/stations")
    if response.status_code == 200:
        return response.json()
    else:
        return []

def get_station_details_by_ids(station_ids):
    all_stations = get_all_stations()
    return [station for station in all_stations if station['id'] in station_ids]
    

def get_trains():
    response = requests.get("http://127.0.0.1:5002/fleet/trains")
    if response.status_code == 200:
        return response.json()
    else:
        return []

def berechne_preise_und_bahnhof_ids(line,percent_profit = 0, price_per_km = 100):
    preise = []
    bahnhof_ids = [line['startStationId']]
    #print(line['sections'])
    for section in line['sections']:
        preis = (round(section['distance'] * price_per_km, 2) + section['fee'])*(1+percent_profit/100) #Presikalkulation kostendeckend + Profitaufschlag
        preise.append(round(preis,2))
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
            print("Error, not Code 200 received")
            # Fehler oder keine Daten gefunden
            return None
    except requests.RequestException as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None
    
def hole_line_prepared(line_id, lines):
    try:
        for line in lines:
            if line["id"] == line_id:
                return line
        # Keine Linie mit der gegebenen ID gefunden
        return None
    except requests.RequestException as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None

def find_next_valid_station_id_and_accumulate(current_index, stations_status, sections):
    accumulated_fee = 0
    accumulated_distance = 0
    next_valid_station_id = None

    # Iterate through the sections, starting from the next index
    for i in range(current_index + 1, len(stations_status)):
        if stations_status[i]:
            next_valid_station_id = stations_status[i]
            break
        else:
            # Accumulate fee and distance for sections marked as False
            accumulated_fee += sections[i]['fee']
            accumulated_distance += sections[i]['distance']

    return next_valid_station_id, accumulated_fee, accumulated_distance

def create_streckenhalteplan(line_data, plan_name, stations_status):
    # Filter out false values and get the first and last station ID
    valid_station_ids = [id for id in stations_status if id]
    if not valid_station_ids:
        raise ValueError("Keine gültigen Stationen ausgewählt.")

    start_station_id = valid_station_ids[0]
    end_station_id = valid_station_ids[-1]
    
    # Create the Streckenhalteplan instance
    new_plan = Streckenhalteplan(name=plan_name, start_station_id=start_station_id, end_station_id=end_station_id, original_line_id=line_data['id'], travel_duration=0.0)
    db.session.add(new_plan)

    # Create Section instances for each section in line_data
    for index, section_data in enumerate(line_data['sections']):
        # Check if the start station of the section is included in the stations_status
        if section_data['startStationId'] in stations_status and section_data['startStationId'] != end_station_id:
            next_valid_station_id, accumulated_fee, accumulated_distance = find_next_valid_station_id_and_accumulate(index, stations_status, line_data['sections'])
            
            new_section = Section(
                startStation=section_data['startStationId'], 
                endStation=next_valid_station_id,
                fee=section_data['fee'] + accumulated_fee, 
                distance=section_data['distance'] + accumulated_distance, 
                maxSpeed=section_data['maxSpeed'], 
                trackWidth=section_data['trackWidth']
            )
            db.session.add(new_section)
            new_plan.sections.append(new_section)

    new_plan.calculate_travel_duration()

    # Commit the changes to the database
    db.session.commit()
    return new_plan.id
