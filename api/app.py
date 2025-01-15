from flask import Flask
from flask_restful import Api, Resource
from dotenv import load_dotenv
import os

load_dotenv()
PORT = os.getenv("PORT")
app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, World!"}

api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
