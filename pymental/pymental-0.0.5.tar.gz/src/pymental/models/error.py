from pymental.meta import Model
from pymental.fields import GenericField, ListField


class Error(Model):
    _tag = 'error_messages'

    code = GenericField('code')
    created_at = GenericField('created_at')
    message = GenericField('message')


class ErrorMessages(Model):
    _tag = 'error_messages'

    errors = ListField('error', Error)

