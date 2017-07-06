from mongoengine import Document, fields

from .group import Group


class Lexicon(Group):
    words = fields.ListField(fields.ReferenceField('Word'))
