import requests
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
PORT = os.getenv("PORT", 6060)
CHARGETRIP_CLIENT_ID = os.getenv("CHARGETRIP_CLIENT_ID", "NONE")
CHARGETRIP_APP_ID = os.getenv("CHARGETRIP_APP_ID", "NONE")

app = Flask(__name__)
api = Api(app)
CORS(app, origins="http://localhost:3000")

#
# RESSOURCES
#

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, World!"}
    
def get_lat_lon(location):
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "VoltWay/1.0"
        }

        response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)

        if response.status_code == 200:
            data = {
                "lat": response.json()[0]["lat"],
                "lon": response.json()[0]["lon"]
            }
            return data
        else:
            print(f"Erreur {response.status_code}: {response.reason}")
            return None

class Itinerary(Resource):
    def get(self):
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        
        if not origin or not destination:
            return {"error": "Missing origin or destination"}, 400
        
        origin_coord = get_lat_lon(origin)
        destination_coord = get_lat_lon(destination)

        if not origin_coord or not destination_coord:
            return {"error": "Cannot get coord from localisation"}, 400

        return {"origin": origin_coord, "destination": destination_coord}, 200

def get_vehicles_data(brand):
    query = """
    query vehicleListAll($brand: String!) {
        vehicleList(search: $brand) {
            id
            naming {
                make
                model
            }
            connectors {
                standard
                time
            }
            range {
                chargetrip_range {
                    best
                    worst
                }
            }
            media {
                image {
                    url
                }
            }
        }
    }
    """
    variables = {
        "brand": brand
    }
    headers = {
        "User-Agent": "VoltWay/1.0",
        "Content-Type": "application/json",
        "x-client-id": CHARGETRIP_CLIENT_ID,
        "x-app-id": CHARGETRIP_APP_ID
    }
    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post("https://api.chargetrip.io/graphql", json=payload, headers=headers)

    if response.status_code == 200:
        vehicles = []
        data = response.json()
        for vehicle in data["data"]["vehicleList"]:
            v = {}
            v['brand'] = vehicle['naming']['make']
            v['model'] = vehicle['naming']['model']
            v['autonomy'] = vehicle['range']['chargetrip_range']['worst']
            v['image'] = vehicle['media']['image']['url']
            charge_time = vehicle['connectors'][0]['time']
            for i in range(1, len(vehicle['connectors'])):
                if charge_time > vehicle['connectors'][i]['time']:
                    charge_time = vehicle['connectors'][i]['time']
            v['charge-time'] = charge_time
            vehicles.append(v)
        return vehicles
    else:
        print(f"Erreur {response.status_code}: {response.reason}")
        return None

class Vehicles(Resource):
    def get(self):
        brand = request.args.get('brand')
        return get_vehicles_data(brand)

#
# ROUTES
#

api.add_resource(HelloWorld, "/helloworld")
api.add_resource(Itinerary, "/itinerary")
api.add_resource(Vehicles, "/vehicles")


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
