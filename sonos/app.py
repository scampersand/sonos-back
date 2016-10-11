from flask import Flask
app = Flask(__name__)

from flask_cors import CORS
CORS(app)  # TODO only allow from same subnet(s) as backend

from flask_restful import Api
api = Api(app)

from .resources.play import CurrentTrack, TransportInfo
from .resources.browse import Browse
from .resources.library import BrowseLibrary, BrowseLibraryArtists
api.add_resource(CurrentTrack, '/current_track')
api.add_resource(TransportInfo, '/transport_info')
api.add_resource(Browse, '/browse/')
api.add_resource(BrowseLibrary, '/browse/library/')
api.add_resource(BrowseLibraryArtists, '/browse/library/artists/')

