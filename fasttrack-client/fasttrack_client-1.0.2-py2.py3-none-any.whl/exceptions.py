
# Bad parameters
class BadParametersException(Exception):
  pass

# Bad request
class BadRequestException(Exception):
  pass

# Internal server error
class InternalServerException(Exception):
  pass

# Invalid version
class InvalidVersionException(Exception):
  pass

# Method not allowed
class MethodNotAllowedException(Exception):
  pass

# No result
class NoResultException(Exception):
  pass

# Not acceptable
class NotAcceptableException(Exception):
  pass

# Not found
class NotFoundException(Exception):
  pass

# Too many requests
class TooManyRequestsException(Exception):
  pass

# Unauthorized
class UnauthorizedException(Exception):
  pass

# Version required
class VersionRequiredException(Exception):
  pass
