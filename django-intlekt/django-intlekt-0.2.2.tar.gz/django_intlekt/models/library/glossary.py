from mongoengine import Document, fields

from .group import Group


class Glossary(Group):
    terms = fields.ListField(fields.StringField(required=True,))
