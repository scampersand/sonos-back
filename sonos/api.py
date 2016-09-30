from flask_restful import Resource
from .sonos import sonos



class CurrentTrack(Resource):
    def get(self):
        return sonos.get_current_track_info()

    def post(self):
        data = request.get_json()
        if not data:  # preflight request
            return ''
        if data['command'] == 'BACK':
            position = sonos.get_current_track_info()['position']
            if position < "0:00:03":
                sonos.previous()
            else:
                sonos.seek("0:00:00")
        elif data['command'] == 'NEXT':
            sonos.next()
        return self.get()


class TransportInfo(Resource):
    def get(self):
        return sonos.get_current_transport_info()

    def post(self):
        data = request.get_json()
        if not data:  # preflight request
            return ''
        if data['command'] == 'PLAY':
            sonos.play()
        elif data['command'] == 'PAUSE':
            sonos.pause()
        elif data['command'] == 'STOP':
            sonos.stop()
        return self.get()


def add_sonos_resources(api):
    api.add_resource(CurrentTrack, '/current_track')
    api.add_resource(TransportInfo, '/transport_info')
