import requests

def get_stations():
    response = requests.get("http://127.0.0.1:5001/route/stations")
    if response.status_code == 200:
        return response.json()
    else:
        return []