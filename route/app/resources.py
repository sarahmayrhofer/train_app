from flask_restful import Resource
from app.models import Station

class StationResource(Resource):
    def get(self):
        stations = Station.query.all()
        return [{
            'id': station.id,
            'nameOfStation': station.nameOfStation,
            'address': station.address,
            'coordinates': station.coordinates
        } for station in stations]
    

