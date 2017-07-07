class KonduktorError(Exception):
    DM = 'An unspecified error occurred.'
    FMT = '{message}'

    def __init__(self, **kwargs):
        kwargs.setdefault('message', self.DM)
        message = self.FMT.format(**kwargs)
        super(KonduktorError, self).__init__(message)


class ClientError(KonduktorError):
    FMT = '[{status_code}] {message}'

    def __init__(self, message=None, status_code=None):
        super(ClientError, self).__init__(message=message, status_code=status_code)
        self.status_code = status_code
        self.message = message


class ResourceValidationError(KonduktorError):
    TEMPLATE = 'Can not process resource: {}.'

    def __init__(self, errors):
        message = self.TEMPLATE.format('; '.join(errors))
        super(ResourceValidationError, self).__init__(message=message)
        self.errors = errors
