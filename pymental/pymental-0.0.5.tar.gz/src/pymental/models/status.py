from pymental.meta import Model
from pymental.fields import GenericField, ListField, RelatedField

from .audit import AuditMessages
from .error import ErrorMessages


class Status(Model):
    _tag = 'job'
    date_format = '%Y-%m-%d %H:%M:%S %z'

    average_fps = GenericField('average_fps')
    elapsed = GenericField('elapsed')
    elapsed_time_in_words = GenericField('elapsed_time_in_words')
    node = GenericField('node')
    pct_complete = GenericField('pct_complete')
    priority = GenericField('priority')
    start_time = GenericField('start_time')
    status = GenericField('status')
    submitted = GenericField('submitted')
    user_data = GenericField('user_data')

    # undocumented fields
    active_input_id = GenericField('active_input_id')
    audit_messages = RelatedField('audit_messages', AuditMessages)
    complete_time = GenericField('complete_time')
    error_messages = RelatedField('error_messages', ErrorMessages)
    errored_time = GenericField('errored_time')
