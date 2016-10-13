from flask import request
from flask_restful import Resource
from ..sonos import sonos
from .. import cache


class CachedResource(Resource):
    max_age = 5

    def get(self):
        value = cache.get(self.cache_key, max_age=self.max_age)
        if value is None:
            value = self._refresh()
            cache.set(self.cache_key, value)
        return value

    def _refresh(self):
        raise NotImplementedError

    @property
    def cache_key(self):
        return self.__class__.__name__



class CurrentTrack(CachedResource):
    _refresh = sonos.get_current_track_info

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


class TransportInfo(CachedResource):
    _refresh = sonos.get_current_transport_info

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
