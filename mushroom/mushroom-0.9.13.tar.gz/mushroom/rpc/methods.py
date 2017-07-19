from .exceptions import RequestValidationError


class Method(object):
    request_serializer = None
    response_serializer = None

    @classmethod
    def as_function(cls):
        def f(request):
            obj = cls()
            return obj(request)
        return f

    def __call__(self, request):
        self.request = request
        self.request_data = self.deserialize_request()
        self.response_data = self.call()
        self.response = self.serialize_response()
        return self.response

    def deserialize_request(self):
        if self.request_serializer:
            serializer = self.request_serializer(data=self.request.data)
            if not serializer.is_valid():
                raise RequestValidationError(serializer.errors)
            return serializer.validated_data
        else:
            return self.request.data

    def serialize_response(self, many=False):
        if self.response_serializer:
            return self.response_serializer(self.response_data, many=many).data
        else:
            return self.response_data


class ListMethod(Method):

    def call(self):
        return self.get_objects()

    def get_objects(self):
        return []


class PaginatedListMethod(ListMethod):
    paginator_min_limit = 1
    paginator_max_limit = None
    paginator_default_limit = None
    paginator_max_offset = None

    def call(self):
        self.paginator_offset = self.request.data.get('offset', 0)
        if isinstance(self.paginator_offset, int):
            if self.paginator_offset < 0:
                # FIXME raise a RequestValidationError?
                self.paginator_offset = 0
        else:
            # FIXME raise a RequestValidationError?
            self.paginator_offset = self.paginator_default_limit
        self.paginator_limit = self.request.data.get('limit', None)
        if isinstance(self.paginator_limit, int):
            if self.paginator_min_limit and self.paginator_limit < self.paginator_min_limit:
                self.paginator_limit = self.paginator_min_limit
            elif self.paginator_max_limit and self.paginator_limit > self.paginator_max_limit:
                self.paginator_limit = self.paginator_max_limit
        else:
            if self.paginator_limit is None:
                self.paginator_limit = self.paginator_max_limit
            else:
                # FIXME raise a RequestValidationError?
                self.paginator_limit = None
        self.all_objects = self.get_objects()
        self.object_count = self.get_object_count()
        self.objects = self.apply_pagination()
        return self.objects

    def get_object_count(self):
        return len(self.all_objects)

    def apply_pagination(self):
        if self.paginator_offset or self.paginator_limit:
            if self.paginator_limit:
                return self.all_objects[:self.paginator_limit]
            else:
                return self.all_objects[self.paginator_offset:self.paginator_offset+self.paginator_limit]
        return self.all_objects

    def serialize_response(self):
        return {
            'list': super(PaginatedListMethod, self).serialize_response(many=True),
            'count': self.object_count
        }
