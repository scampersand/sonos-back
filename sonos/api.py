from flask_restful import Resource, reqparse, inputs
from .sonos import sonos
from . import cache


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


class BrowserResource(Resource):
    envelope_fields = ['title']
    title = 'TITLE'

    def __init__(self, *args, **kwargs):
        super(BrowserResource, self).__init__(*args, **kwargs)
        self.parser = parser = reqparse.RequestParser()
        parser.add_argument('limit', type=inputs.positive, default=100)
        parser.add_argument('start', type=inputs.natural, default=0)

    def parse_args(self):
        return self.parser.parse_args(strict=True)

    def make_envelope(self):
        return {
            name: getattr(self, name)
            for name in self.envelope_fields
        }

    def paged_response(self, items, start, count, total):
        env = self.make_envelope()
        return dict(
            env,
            start=start,
            count=count,
            total=total,
            items=items,
        )

    def one_page_response(self, items):
        return self.paged_response(
            start=0,
            count=len(items),
            total=len(items),
            items=items,
        )


class Browse(BrowserResource):
    title = 'Browse'

    def get(self):
        return self.one_page_response([
            {'path': '/browse/library/', 'title': 'Library'},
        ])


class BrowseLibrary(BrowserResource):
    title = 'Library'

    def get(self):
        return self.one_page_response([
            {'path': '/browse/library/artists/', 'title': 'Artists'},
        ])


class BrowseLibraryArtists(BrowserResource):
    title = 'Artists'

    def get(self):
        args = self.parse_args()
        items = sonos.music_library.get_artists(
            start=args.start,
            max_items=args.limit,
        )
        return self.paged_response(
            start=args.start,  # have to trust it
            count=items.number_returned,
            total=items.total_matches,
            items=[
                {
                    'path': '/browse/library/albums/?id={}'.format(item.item_id),
                    'title': item.title,
                }
                for item in items
            ],
        )


def add_sonos_resources(api):
    api.add_resource(CurrentTrack, '/current_track')
    api.add_resource(TransportInfo, '/transport_info')
    api.add_resource(Browse, '/browse/')
    api.add_resource(BrowseLibrary, '/browse/library/')
    api.add_resource(BrowseLibraryArtists, '/browse/library/artists/')