"""Base pagination iterator for traversing API respones."""


class BasePaginationIterator:

    def __init__(self, client, params=None, limit=None):
        self._client = client
        self.params = params or {}
        self.cursor = None
        self.has_more = True
        self.items = []
        self.limit = limit or 0
        if self.limit > 0:
            if self.limit < 50:
                self.params['limit'] = self.limit
        if limit not in self.params:
            self.params['limit'] = 50

    def parse_resp(self, resp):
        self.items = []

        try:
            self.items = self.parse_data(resp)
        except NotImplementedError:
            self.items = resp['data']

        pagination = resp['pagination']
        self.has_more = pagination['has_more']
        self.cursor = pagination['cursor']
        self.per_page = pagination['per_page']
        self.count = pagination['count']

    def do_req(self, params):
        raise NotImplementedError  # TODO(tsileo): make this one abstract

    def parse_data(self, data):
        """Custom function can return a list of dict/object that will be yield during iteration."""
        raise NotImplementedError

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.items.pop(0)
        except IndexError:
            if not self.has_more:
                raise StopIteration
            params = self.params.copy()
            if self.cursor:
                params['cursor'] = self.cursor
            resp = self.do_req(params)
            self.parse_resp(resp)
            return next(self)
