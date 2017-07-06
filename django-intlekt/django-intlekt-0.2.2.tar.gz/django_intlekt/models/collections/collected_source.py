import uuid

from mongoengine import EmbeddedDocument, fields


class CollectedSource(EmbeddedDocument):
    """A request pattern for a source driver. For instance, all tweets having
    a particular tag. The posts to collect are described in the `params` field,
    the content of which depends on the driver API.
    """

    # To have an immutable identifier for the source
    id = fields.StringField(required=True,)
    driver = fields.ReferenceField('SourceDriver', required=True,)
    params = fields.DictField(
        # Cannot be blank because scrapers need to know which posts to collect
        # on the source
        required=True,
        help_text='A dictionnary of parameters passed to the driver.',
    )
    last_request_date = fields.DateTimeField(null=True,)
    being_requested = fields.BooleanField(default=False,)

    @staticmethod
    def generate_key():
        return uuid.uuid4().hex
