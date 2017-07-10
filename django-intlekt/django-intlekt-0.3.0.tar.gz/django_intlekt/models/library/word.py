from mongoengine import fields

from .usl import USL


class Word(USL):
    is_term = fields.BooleanField(default=False,)
