from ..sonos import sonos
from .browse import BrowserResource


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
