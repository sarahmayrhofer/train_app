from flask_restful import Resource

from fleet.app.models import Train


# Create a resource to handle GET requests for all trains
class AllTrainsResource(Resource):
    def get(self):
        trains = Train.query.all()
        result = []

        for train in trains:
            train_data = {
                'id': train.id,
                'name': train.name,
                'position': train.position,
                'wagons': [],
                'maintenances': []
            }

            # Include wagon information
            for wagon in train.wagons:
                wagon_data = {
                    'id': wagon.id,
                    'track_width': wagon.track_width,
                    'wagon_type': wagon.wagon_type
                }
                train_data['wagons'].append(wagon_data)

            # Include maintenance information
            for maintenance in train.maintenances:
                maintenance_data = {
                    'id': maintenance.id,
                    'description': maintenance.description,
                    # TODO other maintenance fields
                }
                train_data['maintenances'].append(maintenance_data)

            result.append(train_data)

        return {'trains': result}