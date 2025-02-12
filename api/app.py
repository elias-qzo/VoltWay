import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from dotenv import load_dotenv
from resources import Itinerary, Vehicles

load_dotenv()
PORT = os.getenv("PORT", 6060)

app = Flask(__name__)
api = Api(app)
CORS(app)

# Ajout des routes API
api.add_resource(Itinerary, "/itinerary")
api.add_resource(Vehicles, "/vehicles")

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
