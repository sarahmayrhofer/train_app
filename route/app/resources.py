from flask_restful import Resource
from app.models import Station, Section, Event, Line

class StationListResource(Resource):
    def get(self):
        stations = Station.query.all()
        return [{'id': station.id, 'nameOfStation': station.nameOfStation, 'address': station.address, 'coordinates': station.coordinates} for station in stations]

class StationResource(Resource):
    def get(self, id):
        station = Station.query.get(id)
        if station is None:
            return {'error': 'Station not found'}, 404
        return {'id': station.id, 'nameOfStation': station.nameOfStation, 'address': station.address, 'coordinates': station.coordinates}

class SectionListResource(Resource):
    def get(self):
        sections = Section.query.all()
        return [{'id': section.id, 'startStation': section.startStation, 'endStation': section.endStation} for section in sections]

class SectionResource(Resource):
    def get(self, id):
        section = Section.query.get(id)
        if section is None:
            return {'error': 'Section not found'}, 404
        return {'id': section.id, 'startStation': section.startStation, 'endStation': section.endStation}

class EventListResource(Resource):
    def get(self):
        events = Event.query.all()
        return [{'id': event.id, 'section': event.section, 'endDate': event.endDate.isoformat()} for event in events]

class EventResource(Resource):
    def get(self, id):
        event = Event.query.get(id)
        if event is None:
            return {'error': 'Event not found'}, 404
        return {'id': event.id, 'section': event.section, 'endDate': event.endDate.isoformat()}

class LineListResource(Resource):
    def get(self):
        lines = Line.query.all()
        return [{'id': line.id, 'nameOfLine': line.nameOfLine} for line in lines]

class LineResource(Resource):
    def get(self, id):
        line = Line.query.get(id)
        if line is None:
            return {'error': 'Line not found'}, 404
        return {'id': line.id, 'nameOfLine': line.nameOfLine}


