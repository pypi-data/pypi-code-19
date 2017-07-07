from pymental.fields import GenericField, RelatedField
from pymental.meta import Model
from pymental.models import Location


class AppleLiveGroupSettings(Model):
    _tag = 'apple_live_group_settings'

    destination = RelatedField('destination', Location)
    base_url_content = GenericField('base_url_content')
    base_url_manifest = GenericField('base_url_manifest')
    segment_length = GenericField('segment_length')
    min_segment_length = GenericField('min_segment_length')
    emit_single_file = GenericField('emit_single_file')
    floating_point_manifest = GenericField('floating_point_manifest')
    include_resolution = GenericField('include_resolution')
    compress_manifests = GenericField('compress_manifests')
    use_subdirectories = GenericField('use_subdirectories')
    segments_per_subdirectory = GenericField('segments_per_subdirectory')
    insert_program_date_time = GenericField('insert_program_date_time')
    timed_metadata_id3_period = GenericField('timed_metadata_id3_period')
    timed_metadata_id3_frame = GenericField('timed_metadata_id3_frame')
    program_date_time_period = GenericField('program_date_time_period')
    cdn = GenericField('cdn')
    connection_retry_interval = GenericField('connection_retry_interval')
    generate_meta_file = GenericField('generate_meta_file')
    vod_mode = GenericField('vod_mode')
    num_retries = GenericField('num_retries')
    filecache_duration = GenericField('filecache_duration')
    alternate_manifest_destination = GenericField(
        'alternate_manifest_destination')  # TODO: map to model
    encryption_type = GenericField('encryption_type')
    caption_language_setting = GenericField('caption_language_setting')
    key_rotation_count = GenericField('key_rotation_count')
    show_iv = GenericField('show_iv')
    iv_follows_segment_number = GenericField('iv_follows_segment_number')
    constant_iv = GenericField('constant_iv')
    key_provider_settings = GenericField('key_provider_settings')
    key_format = GenericField('key_format')
    key_format_versions = GenericField('key_format_versions')
    key_save_location = RelatedField('key_save_location', Location)
    key_prefix = GenericField('key_prefix')
    ad_markers = GenericField('ad_markers')
    disable_cache = GenericField('disable_cache')
    use_pantos_7_codecs = GenericField('use_pantos_7_codecs')
    policy_file = RelatedField('policy_file', Location)
    swf_identifiers_file = RelatedField('swf_identifiers_file', Location)


class FileGroupSettings(Model):
    _tag = 'file_group_settings'

    destination = RelatedField('destination', Location)
    rollover_interval = GenericField('rollover_interval')
