from flask_restful import Resource
from app.models import Station, Section, Event, Line

# In this file, the resources for the RESTful API are defined. The paths are specified in the __init__.py file in the route/app folder.

class StationListResource(Resource):
    def get(self):
        stations = Station.query.all()
        return [{'id': station.id, 'nameOfStation': station.nameOfStation, 'address': station.address, 'coordinates': station.coordinates} for station in stations]


class SectionListResource(Resource):
    def get(self):
        sections = Section.query.all()
        return [{'id': section.id, 'startStationId': section.startStation, 'endStationId': section.endStation, 'fee': section.fee, 'distance': section.distance, 'maxSpeed': section.maxSpeed, 'trackWidth': section.trackWidth} for section in sections]


class EventListResource(Resource):
    def get(self):
        events = Event.query.all()
        return [{'id': event.id, 'sectionId': event.section, 'endDate': event.endDate.isoformat() if event.endDate else None, 'officialText': event.officialText, 'internalText': event.internalText} for event in events]

class LineListResource(Resource):
    def get(self):
        lines = Line.query.all()
        return [{'id': line.id, 'nameOfLine': line.nameOfLine, 'startStationId': line.startStation.id if line.startStation else None, 'endStationId': line.endStation.id if line.endStation else None, 'sections': [{'id': section.id, 'startStationId': section.startStation, 'endStationId': section.endStation, 'fee': section.fee, 'distance': section.distance, 'maxSpeed': section.maxSpeed, 'trackWidth': section.trackWidth} for section in line.sections]} for line in lines]