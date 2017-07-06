from mongoengine import Document, fields


class SourceDriver(Document):
    """A service to pull posts from a source."""

    source = fields.ReferenceField('Source', required=True,)
    url = fields.URLField(unique=True, required=True,)
