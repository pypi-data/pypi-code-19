from mongoengine import Document as MEDocument, fields


class Document(MEDocument):
    """A document on the web.

    Most fields can be null because scrapers may not be able to detect them
    automatically. Users will edit them afterwards.
    """

    title = fields.StringField(
        null=True,
        help_text='Null if unknown.',
    )
    authors = fields.ListField(fields.StringField(),)
    created_on = fields.DateTimeField(
        null=True,
        help_text='Null if unknown.',
    )
    # Not unique because a single web page can contain multiple documents
    url = fields.URLField(required=True,)
    keywords = fields.ListField(fields.StringField(),)
    language = fields.StringField(
        null=True,
        help_text='Use the ISO 639-1 format. Null if unknown.',
    )

    def __str__(self):
        return self.title
