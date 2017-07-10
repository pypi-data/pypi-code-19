from mongoengine import fields

from .usl import USL


class Text(USL):
    dependencies = fields.ListField(fields.ReferenceField('USL'), required=True,)
