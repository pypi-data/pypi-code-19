class ResourceNotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class IntegrityError(Exception):
    pass


class ConflictError(Exception):
    pass


class UnexpectedError(Exception):
    pass
