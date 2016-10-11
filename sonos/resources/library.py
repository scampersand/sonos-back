from urllib.parse import urlencode
from ..sonos import sonos
from .browse import BrowserResource


class BrowseLibrary(BrowserResource):
    title = 'Library'

    def get(self):
        return self.one_page_response([
            {'path': '/browse/library/artists/', 'title': 'Artists'},
        ])


class LibraryResource(BrowserResource):

    def _get(self, search_type, args, **kwargs):
        return sonos.music_library.get_music_library_information(
            search_type,
            start=args.start,
            max_items=args.limit,
            **kwargs
        )


class BrowseLibraryArtists(LibraryResource):
    title = 'Artists'

    def get(self):
        args = self.parse_args()
        items = self._get('artists', args)
        return self.paged_response(
            start=args.start,  # have to trust it
            count=items.number_returned,
            total=items.total_matches,
            items=[
                {
                    'path': '/browse/library/albums/?{}'.format(
                        urlencode([('artist', item.title)])),
                    'title': item.title,
                }
                for item in items
            ],
        )


class BrowseLibraryAlbums(LibraryResource):
    title = 'Albums'

    def get_parser(self):
        parser = super(BrowseLibraryAlbums, self).get_parser()
        parser.add_argument('artist')
        return parser

    def get(self):
        args = self.parse_args()
        items = (self._get('artists', args, subcategories=[args.artist])
                 if args.artist else self._get('albums', args))
        return self.paged_response(
            start=args.start,  # have to trust it
            count=items.number_returned,
            total=items.total_matches,
            items=[
                {
                    'path': '/play/this/album/?{}'.format(
                        urlencode([('artist', item.creator),
                                   ('album', item.title)])),
                    'artist': item.creator,
                    'title': item.title,
                }
                for item in items
                if hasattr(item, 'creator')  # exclude DidlSameArtist ("All Tracks")
            ],
        )