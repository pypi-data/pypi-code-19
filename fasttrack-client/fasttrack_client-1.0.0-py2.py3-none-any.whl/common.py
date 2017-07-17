
from .exceptions import *

ERRORS_BY_STATUS = {
  '400' : BadRequestException,
  '401' : UnauthorizedException,
  '404' : NotFoundException,
  '405' : MethodNotAllowedException,
  '406' : NotAcceptableException,
  '429' : TooManyRequestsException
}

ERRORS_BY_ERROR_CODE = {
  '1' : VersionRequiredException,
  '2' : NoResultException,
  '3' : BadParametersException,
  '4' : InvalidVersionException
}

def exceptionForResponse(status, errorCode):
  fastTrackError = None

  if errorCode != None:
    fastTrackError = ERRORS_BY_ERROR_CODE.get(errorCode, None)

  if fastTrackError == None and status != None:
    fastTrackError = ERRORS_BY_STATUS.get(str(status), None)

    if status >= 500 and status < 600:
      fastTrackError = InternalServerException

  if fastTrackError == None:
    fastTrackError = Exception

  return fastTrackError
