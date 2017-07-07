from pymental.meta import Model
from pymental.fields import GenericField


class ContentDuration(Model):
    _tag = 'content_duration'

    clipped_input_duration = GenericField('clipped_input_duration')
    input_duration = GenericField('input_duration')
    package_count = GenericField('package_count')
    stream_count = GenericField('stream_count')
    total_package_duration = GenericField('total_package_duration')
    total_stream_duration = GenericField('total_stream_duration')
