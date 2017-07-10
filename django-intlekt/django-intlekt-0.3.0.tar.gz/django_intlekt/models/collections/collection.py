from django.utils import timezone
from mongoengine import Document, fields, signals


class Collection(Document):
    """A coherent group of documents gathered by a user."""

    title = fields.StringField(unique=True, required=True,)
    curators = fields.ListField(fields.StringField(), required=True,)
    created_on = fields.DateTimeField(default=timezone.now,)
    updated_on = fields.DateTimeField(default=timezone.now,)
    # Use a MapField instead of a ListField to ensure that a document is not
    # collected more than once
    posts = fields.MapField(
        fields.EmbeddedDocumentField('Post'),
        help_text="The key must be equal to the 'document' field of the post.",
    )
    # Use a MapField to retrieve a source from its id efficiently.
    # Also make sure that ids are unique.
    sources = fields.MapField(
        fields.EmbeddedDocumentField('CollectedSource'),
        help_text="The key must be equal to the 'id' field of the collected source.",
    )

    meta = {
        'ordering': ['title'],
    }

    def __str__(self):
        return self.title

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_on = timezone.now()

        for key, source in document.sources.items():
            if key:
                continue

            document.sources.pop(key)
            key = source.generate_key()
            source.id = key
            document.sources[key] = source


signals.pre_save.connect(Collection.pre_save, sender=Collection)
