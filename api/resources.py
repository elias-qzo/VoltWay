from flask import request
from flask_restful import Resource
from services import get_lat_lon, get_waypoints, get_full_trip, add_charging, get_charging_stations_trip
import requests
import os

CHARGETRIP_CLIENT_ID = os.getenv("CHARGETRIP_CLIENT_ID", "NONE")
CHARGETRIP_APP_ID = os.getenv("CHARGETRIP_APP_ID", "NONE")

class Itinerary(Resource):
    def get(self):
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        autonomy = request.args.get('autonomy')
        loadTime = request.args.get('load_time')
        
        if not origin or not destination or not autonomy:
            return {"error": "Missing origin, destination or autonomy"}, 400
        
        origin_coord = get_lat_lon(origin)
        destination_coord = get_lat_lon(destination)
        
        if not origin_coord or not destination_coord:
            return {"error": "Cannot get coordinates from location"}, 400
        
        initial_waypoints = get_waypoints(origin_coord, destination_coord)
        if not initial_waypoints:
            return {"error": "Cannot get waypoints"}, 400
        
        charging_stations_waypoints = get_charging_stations_trip(initial_waypoints, autonomy)
        trip_waypoints = charging_stations_waypoints.copy()
        trip_waypoints.insert(0, [origin_coord["lon"], origin_coord["lat"]])
        trip_waypoints.append([destination_coord["lon"], destination_coord["lat"]])
        
        full_trip = get_full_trip(trip_waypoints)
        if not full_trip:
            return {"error": "Failed to generate full trip"}, 400
        
        full_trip["charging_stations"] = charging_stations_waypoints
        full_trip = add_charging(full_trip, loadTime, autonomy)
        
        return full_trip, 200

class Vehicles(Resource):
    def get(self):
        brand = request.args.get('brand')
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
        variables = {"brand": brand}
        headers = {
            "User-Agent": "VoltWay/1.0",
            "Content-Type": "application/json",
            "x-client-id": CHARGETRIP_CLIENT_ID,
            "x-app-id": CHARGETRIP_APP_ID
        }
        response = requests.post("https://api.chargetrip.io/graphql", json={"query": query, "variables": variables}, headers=headers)
        
        if response.status_code == 200:
            vehicles = []
            data = response.json()
            for vehicle in data["data"].get("vehicleList", []):
                v = {
                    'brand': vehicle['naming']['make'],
                    'model': vehicle['naming']['model'],
                    'autonomy': vehicle['range']['chargetrip_range']['worst'],
                    'image': vehicle['media']['image']['url'],
                    'charge-time': min(connector['time'] for connector in vehicle['connectors'])
                }
                vehicles.append(v)
            return vehicles, 200
        else:
            return {"error": f"Request failed with status {response.status_code}"}, 400
