from pymental.meta import Model
from pymental.fields import GenericField, ListField, RelatedField, SKIP

from .audit import AuditMessages
from .content_duration import ContentDuration
from .error import ErrorMessages
from .input import Input
from .notification import Notification
from .output import Output, OutputGroup
from .process import PreProcess, PostProcess
from .stream_assembly import StreamAssembly
from .timecode_config import TimecodeConfig


class BaseJob(Model):

    ad_avail_offset = GenericField('ad_avail_offset')
    ad_trigger = GenericField('ad_trigger')
    avail_blanking = GenericField('avail_blanking')
    avsync_enable = GenericField('avsync_enable')
    avsync_pad_trim_audio = GenericField('avsync_pad_trim_audio')
    image_inserter = GenericField('image_inserter')
    input = RelatedField('input', Input)
    nielsen_configuration = GenericField('nielsen_configuration')
    notification = RelatedField('notification', Notification)
    output_groups = ListField('output_group', OutputGroup)
    post_process = RelatedField('post_process', PostProcess)
    postroll_input = RelatedField('postroll_input', Input)
    pre_process = RelatedField('pre_process', PreProcess)
    preroll_input = RelatedField('preroll_input', Input)
    priority = GenericField('priority')
    streams = ListField('stream_assembly', StreamAssembly)
    timecode_config = RelatedField('timecode_config', TimecodeConfig)
    user_data = GenericField('user_data')

    class Meta:
        abstract = True

    @property
    def id(self):
        href = self._attributes.get('href')
        return href.split('/')[-1] if href else None

    def get_all_outputs(self):
        outputs = []
        if self.output_groups is not SKIP:
            for output_group in self.output_groups:
                outputs.extend(output_group.outputs)
        return outputs


class Job(BaseJob):
    _tag = 'job'

    active_input_id = GenericField('active_input_id')
    audit_messages = RelatedField('audit_messages', AuditMessages)
    average_fps = GenericField('average_fps')
    complete_time = GenericField('complete_time')
    content_duration = RelatedField('content_duration', ContentDuration)
    elapsed = GenericField('elapsed')
    error_messages = RelatedField('error_messages', ErrorMessages)
    errored_time = GenericField('errored_time')
    esam = GenericField('esam')
    motion_image_inserter = GenericField('motion_image_inserter')
    node = GenericField('node')
    node_id = GenericField('node_id')
    pct_complete = GenericField('pct_complete')
    profile = GenericField('profile',
                           description='Valid Profile ID, name, or permalink')
    server_output = RelatedField('server_output', Output)
    start_time = GenericField('start_time')
    status = GenericField('status')
    submitted = GenericField('submitted')

    def __repr__(self):
        return '<{} #{}>'.format(self.__class__.__name__, self.id)

    def get_all_error_messages(self):
        if self.error_messages is not SKIP:
            return [error.message for error in self.error_messages.errors]
        return []


class JobProfile(BaseJob):
    _tag = 'job_profile'

    name = GenericField('name')
    description = GenericField('description')
    permalink = GenericField('permalink')
