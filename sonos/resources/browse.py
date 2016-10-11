from flask_restful import Resource, reqparse, inputs


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