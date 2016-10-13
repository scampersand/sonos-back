from flask_restful import Resource, reqparse, inputs


class BrowserResource(Resource):
    envelope_fields = ['title']
    title = 'TITLE'

    def get_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=inputs.positive, default=100)
        parser.add_argument('start', type=inputs.natural, default=0)
        return parser

    def parse_args(self):
        return self.get_parser().parse_args(strict=True)

    def make_envelope(self):
        return {
            name: getattr(self, name)
            for name in self.envelope_fields
        }

    def paged_response(self, items, start, count, total):
        return dict(
            self.make_envelope(),
            start=start,
            count=count,
            total=total,
            items=items,
        )

    def simple_paged_response(self, items):
        args = self.parse_args()
        total = len(items)
        if args.start or args.limit < len(items):
            items = items[args.start:args.start+args.limit]
        return self.paged_response(
            start=args.start,
            count=len(items),
            total=total,
            items=items,
        )


class Browse(BrowserResource):
    title = 'Browse'

    def get(self):
        return self.simple_paged_response([
            {'path': '/browse/library/', 'title': 'Music Library'},
        ])
