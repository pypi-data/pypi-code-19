from pymental.fields import GenericField
from pymental.meta import Model


class TimecodeConfig(Model):
    _tag = 'timecode_config'

    source = GenericField('source')
    start = GenericField('start')
    anchor = GenericField('anchor')
    require_initial_timecode = GenericField('require_initial_timecode')
    override_timecode_date = GenericField('override_timecode_date')
    sync_threshold = GenericField('sync_threshold')
    timestamp_offset = GenericField('timestamp_offset')
