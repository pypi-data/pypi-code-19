class BaseRepresentation:
    SCHEMA = None
    RESOURCE = None

    def __init__(self, document, filename, search_api=True):
        document, errors = self.SCHEMA().load(document)
        if errors:
            raise ValueError(errors)
        self.document = document
        self.filename = filename
        self._search_api = search_api
        self.ids = [] # Where to store
        if search_api:
            self.ids = self._search_api_for_duplicates()
        self._dependencies = None

    def _search_api_for_duplicates(self):
        raise NotImplementedError()

    def determine_dependencies(self, candidates):
        raise NotImplementedError()

    @property
    def resource_items(self):
        return [self.RESOURCE(id) for id in self.ids]

    @property
    def dependencies(self):
        if self._dependencies is None:
            raise ValueError('Must call determine dependencies first')
        return self._dependencies

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.filename}>'
