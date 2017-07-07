from pymental.fields import GenericField, RelatedField
from pymental.meta import Model

from .location import Location


class Input(Model):
    _tag = 'input'

    file_input = RelatedField('file_input', Location)
    order = GenericField('order')
    program_id = GenericField('program_id')
    deblock_enable = GenericField('deblock_enable')
    deblock_strength = GenericField('deblock_strength')
    no_psi = GenericField('no_psi')
    input_clipping = GenericField('input_clipping')
    video_selector = GenericField('video_selector')
    audio_selector = GenericField('audio_selector')
    audio_selector_group = GenericField('audio_selector_group')
    caption_selector = GenericField('caption_selector')
    timecode_source = GenericField('timecode_source')
    authentication_details = GenericField('authentication_details')
    name = GenericField('name')  # extra field, not in docs

