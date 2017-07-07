from pymental.meta import Model
from pymental.fields import GenericField, ListField


class Audit(Model):
    _tag = 'audit'

    code = GenericField('code')
    created_at = GenericField('created_at')
    data = GenericField('data')
    message = GenericField('message')


class AuditMessages(Model):
    _tag = 'audit_messages'

    messages = ListField('audit', Audit)


