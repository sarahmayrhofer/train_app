from datetime import datetime


def idToStation(id):
    return {1:"Linz", 2:"Wien", 3:"Salzburg", 4:"Graz", 5:"Innsbruck", 6:"Klagenfurt", 7:"Bregenz"}[id]

#Wien Hbf -> St. Pölten Hbf -> Linz Hbf -> Wels Hbf
#direkten

travelroutes = {
    "travel_id": 1,
    "name": "Westbahnstrecke", 
    "sections": [
        {
            "id": 1,
            "start_station_id": 1,
            "end_station_id": 2,
            "price": 10,
            "duration": 100,
        },
        {
            "id": 2,
            "start_station_id": 2,
            "end_station_id": 3,
            "fee": 10,
            "distance": 100,
        },
        {
            "id": 3,
            "start_station_id": 3,
            "end_station_id": 4,
            "fee": 10,
            "distance": 100,
        },
     
    ]
}

"""
Wien Hbf -> St. Pölten Hbf
Wien Hbf -> Linz Hbf
Wien Hbf -> Wels Hbf
St. Pölten Hbf -> Linz Hbf
St. Pölten Hbf -> Wels Hbf
Linz Hbf -> Wels Hbf
"""

#lassen sich von routes ableiten
connections = [
    {
        "id": 1,
        "start_station_id": 1,
        "start_station_name": "Wien Hbf",
        "end_station_id": 2,
        "end_station_name": "St. Pölten Hbf",
        "route_id": 1,
    },
    {
        "id": 2,
        "start_station_id": 1,
        "start_station_name": "Wien Hbf",
        "end_station_id": 3,
        "end_station_name": "Linz Hbf",
        "route_id": 1,
    },
    {
        "id": 3,
        "start_station_id": 1,
        "start_station_name": "Wien Hbf",
        "end_station_id": 4,
        "end_station_name": "Wels Hbf",
        "route_id": 1,
    },
    {
        "id": 4,
        "start_station_id": 2,
        "start_station_name": "St. Pölten Hbf",
        "end_station_id": 3,
        "end_station_name": "Linz Hbf",
        "route_id": 1,
    },
    {
        "id": 5,
        "start_station_id": 2,
        "start_station_name": "St. Pölten Hbf",
        "end_station_id": 4,
        "end_station_name": "Wels Hbf",
        "route_id": 1,
    },
    {
        "id": 6,
        "start_station_id": 3,
        "start_station_name": "Linz Hbf",
        "end_station_id": 4,
        "end_station_name": "Wels Hbf",
        "route_id": 1,
    }
]

#generelle Strecke, Connection - örtliche Abfrage, von bis, gibt es das?, bestimmte Zeit Durchführung, Trips, 

trips = [
    {
        "id": 1,
        "name": "L",
        "arrival_time": "2022-12-02T08:00:00",
        "departure_time": "2022-12-01T08:30:00",
        "route_id": 1
    },
    {
        "id": 2,
        "name": "S",
        "arrival_time": "2022-12-01T09:00:00",
        "departure_time": "2022-12-01T09:30:00",
        "route_id": 1
    },
    {
        "id": 3,
        "name": "Y",
        "arrival_time": "2022-12-01T10:00:00",
        "departure_time": "2022-12-01T10:30:00",
        "route_id": 1
    },
    {
        "id": 4,
        "name": "Wien",
        "arrival_time": "2022-12-01T11:00:00",
        "departure_time": "2022-12-01T11:30:00",
        "route_id": 1
    },
    {
        "id": 5,
        "name": "Linz",
        "arrival_time": "2022-12-02T08:00:00",
        "departure_time": "2022-12-02T08:30:00",
        "route_id": 1
    },
    {
        "id": 6,
        "name": "Z",
        "arrival_time": "2022-12-02T09:00:00",
        "departure_time": "2022-12-02T09:30:00",
        "route_id": 1
    },
    {
        "id": 7,
        "name": "K",
        "arrival_time": "2022-12-02T10:00:00",
        "departure_time": "2022-12-02T10:30:00",
        "route_id": 1
    },
    {
        "id": 8,
        "name": "Wien",
        "arrival_time": "2022-12-02T11:00:00",
        "departure_time": "2022-12-02T11:30:00",
        "route_id": 1
    },
    {
        "id": 9,
        "name": "Linz",
        "arrival_time": "2022-12-01T12:00:00",
        "departure_time": "2022-12-01T12:30:00",
        "route_id": 1
    }
]




def get_trips_by_date_and_time(trips, date, time):
    # Combine date and time into a datetime string
    datetime_str = f"{date}T{time}"
    
    # Convert the datetime string into a datetime object
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
    print(datetime_obj)

    # Filter the trips that have an arrival time greater than or equal to the given datetime
    filtered_trips = [trip for trip in trips if datetime.strptime(trip['departure_time'], "%Y-%m-%dT%H:%M:%S") >= datetime_obj]

    return filtered_trips

resu = get_trips_by_date_and_time(trips, "2022-12-01", "10:00:00")
print(resu)


print("--------------------------------------------------")
print("extra")
def get_trips_by_date_time_and_stations(trips, connections, date, time, start_station_name, end_station_name):
    # Combine date and time into a datetime string
    datetime_str = f"{date}T{time}"
    
    # Convert the datetime string into a datetime object
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
    print(f"{datetime_obj.hour}:{datetime_obj.minute}")

    # Filter the connections that match the start and end station
    filtered_connections = [connection for connection in connections if connection['start_station_name'] == start_station_name and connection['end_station_name'] == end_station_name]

    # Filter the trips that have a departure time greater than or equal to the given datetime and match the filtered connections
    filtered_trips = [trip for trip in trips if datetime.strptime(trip['departure_time'], "%Y-%m-%dT%H:%M:%S") >= datetime_obj and trip['route_id'] in [connection['route_id'] for connection in filtered_connections]]

    return filtered_trips

resu = get_trips_by_date_time_and_stations(trips, connections, "2022-12-01", "10:00:00", "Wien Hbf", "Linz Hbf")
print(resu)

for trip in resu:
    print(f"Trip ID: {trip['id']}")
    print(f"Name: {trip['name']}")
    print(f"Arrival Time: {trip['arrival_time']}")
    print(f"Departure Time: {trip['departure_time']}")
    print(f"Route ID: {trip['route_id']}")
    print("------------------------")