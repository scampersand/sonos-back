from flask import Flask
app = Flask(__name__)

from flask_cors import CORS
CORS(app)  # TODO only allow from same subnet(s) as backend

from flask_restful import Api
api = Api(app)

from .api import add_sonos_resources
add_sonos_resources(api)

