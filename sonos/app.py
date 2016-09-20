from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api
import soco

app = Flask(__name__)
CORS(app)  # TODO only allow from same subnet(s) as backend
api = Api(app)

sonos = soco.SoCo("172.20.1.233")


class TrackInfo(Resource):
    def get(self):
        return sonos.get_current_track_info()

api.add_resource(TrackInfo, '/track_info')


class TransportState(Resource):
    def get(self):
        return {'current_transport_state':
                sonos.get_current_transport_info()['current_transport_state']}

    def put(self):
        data = request.get_json()
        if not data:  # preflight request
            return ''
        if data['current_transport_state'] == 'PLAYING':
            sonos.play()
        elif data['current_transport_state'] == 'PAUSED_PLAYBACK':
            sonos.pause()
        elif data['current_transport_state'] == 'STOPPED':
            sonos.stop()
        return {'current_transport_state': data['current_transport_state']}

api.add_resource(TransportState, '/transport_state')
