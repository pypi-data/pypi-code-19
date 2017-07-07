from pymental.fields import GenericField
from pymental.meta import Model


class StreamAssembly(Model):
    _tag = 'stream_assembly'

    name = GenericField('name')
    video_description = GenericField('video_description')
    audio_description = GenericField('audio_description')
    caption_description = GenericField('caption_description')
    preset = GenericField('preset', description='A valid Preset ID or name')
