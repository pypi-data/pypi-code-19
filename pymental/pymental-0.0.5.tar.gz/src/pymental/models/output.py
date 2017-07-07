from pymental.fields import GenericField, ListField, RelatedField
from pymental.meta import Model

from .group_settings import FileGroupSettings, AppleLiveGroupSettings


class Output(Model):
    _tag = 'output'

    apple_live_settings = GenericField('apple_live_settings')
    container = GenericField('container')
    description = GenericField('description')
    ebif_passthrough = GenericField('ebif_passthrough')
    extension = GenericField('extension')
    f4v_settings = GenericField('f4v_settings')
    full_uri = GenericField('full_uri')
    id = GenericField('id')
    insert_scte35_esam = GenericField('insert_scte35_esam')
    insert_timed_metadata = GenericField('insert_timed_metadata')
    klv_passthrough = GenericField('klv_passthrough')
    log_edit_points = GenericField('log_edit_points')
    m2ts_settings = GenericField('m2ts_settings')
    m3u8_settings = GenericField('m3u8_settings')
    mov_settings = GenericField('mov_settings')
    mp4_settings = GenericField('mp4_settings')
    name_modifier = GenericField('name_modifier')
    order = GenericField('order')
    preset_id = GenericField('preset_id')
    raw_settings = GenericField('raw_settings')
    scte35_passthrough = GenericField('scte35_passthrough')
    stream_assembly_name = GenericField('stream_assembly_name')
    uvu_settings = GenericField('uvu_settings')
    nielsen_id3_passthrough = GenericField('nielsen_id3_passthrough')
    # start_paused = GenericField('start_paused', default=False)  # noqa documented but not accepted


class OutputGroup(Model):
    _tag = 'output_group'

    type = GenericField('type')
    name = GenericField('name')
    custom_name = GenericField('custom_name')
    order = GenericField('order')
    file_group_settings = RelatedField('file_group_settings', FileGroupSettings)
    apple_live_group_settings = RelatedField(
        'apple_live_group_settings', AppleLiveGroupSettings)
    dash_iso_group_settings = GenericField('dash_iso_group_settings')
    hds_group_settings = GenericField('hds_group_settings')
    ms_smooth_group_settings = GenericField('ms_smooth_group_settings')
    outputs = ListField('output', Output)
