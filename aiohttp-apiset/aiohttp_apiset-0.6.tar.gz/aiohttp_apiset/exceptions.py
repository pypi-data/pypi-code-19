from aiohttp.web_exceptions import HTTPBadRequest


class ValidationError(HTTPBadRequest):
    pass
