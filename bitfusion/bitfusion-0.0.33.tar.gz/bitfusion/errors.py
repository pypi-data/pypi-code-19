class BitfusionError(Exception):
  pass


"""
Errors from HTTP calls into the platform
"""
class HTTPError(BitfusionError):
  pass

class ClientError(HTTPError):
  pass

class AuthError(HTTPError):
  pass

class NotFoundError(HTTPError):
  pass

class PermissionError(HTTPError):
  pass

class PlatformError(HTTPError):
  pass
