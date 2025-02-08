import requests
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from dotenv import load_dotenv
from geopy.distance import geodesic
import os
import openrouteservice

load_dotenv()
PORT = os.getenv("PORT", 6060)
CHARGETRIP_CLIENT_ID = os.getenv("CHARGETRIP_CLIENT_ID", "NONE")
CHARGETRIP_APP_ID = os.getenv("CHARGETRIP_APP_ID", "NONE")
ORS_API_KEY = os.getenv("ORS_API_KEY", "NONE")

API_REQUEST_HEADER = {
    "User-Agent": "VoltWay/1.0"
}

app = Flask(__name__)
api = Api(app)
CORS(app)

#
# RESSOURCES
#

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, World!"}
    
def get_lat_lon(location):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }

        response = requests.get(url, params=params, headers=API_REQUEST_HEADER)

        if response.status_code == 200:
            data = {
                "lat": float(response.json()[0]["lat"]),
                "lon": float(response.json()[0]["lon"])
            }
            return data
        else:
            print(f"Error {response.status_code}: {response.reason}")
            return None
        

def get_waypoints(origin, destination):
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        params = {
            "api_key": ORS_API_KEY,
            "start": str(origin["lon"])+","+str(origin["lat"]),
            "end": str(destination["lon"])+","+str(destination["lat"])
        }

        response = requests.get(url, params=params, headers=API_REQUEST_HEADER)

        if response.status_code == 200:
            data = response.json()["features"][0]["geometry"]["coordinates"]
            return data
        else:
            print(f"Error {response.status_code}: {response.reason}")
            return None

        
def get_charging_stations_trip(waypoints, autonomy):
    distance = 0
    autonomy = int(autonomy)
    autonomy *= 1000
    autonomy -= 1500 # 1.5 km to find a charging station
    charging_stations = []
    for i in range(len(waypoints) - 2):
        distance += geodesic((waypoints[i][1], waypoints[i][0]), (waypoints[i+1][1], waypoints[i+1][0])).meters
        if distance >= autonomy:
            print(distance)
            print("CHARGING")
            closest_station = find_closest_charging_stations({"lat": waypoints[i][1], "lon" : waypoints[i][0]})
            charging_stations.append(closest_station)
            distance = 0
    distance /= 1000
    return charging_stations
    
def find_closest_charging_stations(point):
        url = "https://public.opendatasoft.com/api/records/1.0/search"
        radius = 20000 # meters
        params = {
            "geofilter.distance": str(point["lat"])+","+str(point["lon"])+","+str(radius),
            "dataset" : "osm-france-charging-station"
        }

        response = requests.get(url, params=params, headers=API_REQUEST_HEADER)
        if response.status_code == 200:
            stations = response.json()['records']
        else:
            print(f"Error {response.status_code}: {response.reason}")
            return None
        
        if not stations:
            print("No stations")
            return None
        return stations[0]["geometry"]["coordinates"]

def get_full_trip(waypoints):
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        params = {
            "api_key": ORS_API_KEY,
        }
        json = {
            "coordinates": waypoints,
        }
        response = requests.post(url, params=params, json=json, headers=API_REQUEST_HEADER)

        if response.status_code == 200:
            data = {}
            decoded_geometry = openrouteservice.convert.decode_polyline(response.json()["routes"][0]["geometry"])
            data["bbox"] = response.json()["bbox"]
            data["summary"] = response.json()["routes"][0]["summary"]
            data["waypoints"] = decoded_geometry["coordinates"]
            return data
        else:
            print(f"Error {response.status_code}: {response.reason}")
            return None


class Itinerary(Resource):
    def get(self):
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        autonomy = request.args.get('autonomy')
        
        if not origin or not destination or not autonomy:
            return {"error": "Missing origin, destination or autonomy"}, 400
        
        origin_coord = get_lat_lon(origin)
        destination_coord = get_lat_lon(destination)

        if not origin_coord or not destination_coord:
            return {"error": "Cannot get coord from localisation"}, 400
        
        initial_waypoints = get_waypoints(origin_coord,destination_coord)

        if not initial_waypoints:
            return {"error": "Cannot get waypoints"}, 400
        
        charging_stations_waypoints = get_charging_stations_trip(initial_waypoints, autonomy)
        trip_waypoints = charging_stations_waypoints.copy()
        trip_waypoints.insert(0,[origin_coord["lon"],origin_coord["lat"]])
        trip_waypoints.append([destination_coord["lon"],destination_coord["lat"]])
        full_trip = get_full_trip(trip_waypoints)
        full_trip["charging_stations"] = charging_stations_waypoints

        return full_trip, 200

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
