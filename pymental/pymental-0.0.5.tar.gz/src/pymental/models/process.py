from pymental.fields import GenericField, RelatedField
from pymental.meta import Model
from pymental.models import Location


class PreProcess(Model):
    script = RelatedField('script', Location)
    progressive_reader_setting = GenericField('progressive_reader_setting')


class PostProcess(Model):
    delete_source = GenericField('delete_source')
    delete_source_dir = GenericField('delete_source_dir')
    processed = RelatedField('processed', Location)
    script = RelatedField('script', Location)
