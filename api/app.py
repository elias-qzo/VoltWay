import requests
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
PORT = os.getenv("PORT", 6060)

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
            print(data)
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

#
# ROUTES
#

api.add_resource(HelloWorld, "/helloworld")
api.add_resource(Itinerary, "/itinerary")


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
