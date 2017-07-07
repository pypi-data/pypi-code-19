from pymental.fields import GenericField
from pymental.meta import Model


class Notification(Model):
    _tag = 'notification'

    email = GenericField('email')
    web_callback_url = GenericField('web_callback_url')
    on_started = GenericField('on_started')
    on_complete = GenericField('on_complete')
    on_error = GenericField('on_error')
    on_warning = GenericField('on_warning')
    on_cancel = GenericField('on_cancel')
