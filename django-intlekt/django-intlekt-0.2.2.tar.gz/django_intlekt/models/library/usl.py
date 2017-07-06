from mongoengine import Document, fields


class USL(Document):
    ieml_text = fields.StringField(unique=True, required=True,)
    # Can be blank because a USL attached to a post is likely to be the
    # union of the tags, with no particular translation in natural language.
    translations = fields.MapField(
        fields.StringField(),
        help_text=('Translations in natural languages. '
                   'Use the ISO 639-1 format for the keys.'),
    )

    meta = {
        'ordering': ['ieml_text'],
        'indexes': [
            'ieml_text',
        ],
        'allow_inheritance': True,
    }

    def __str__(self):
        return '{0}: {1}'.format(
            self.__class__.__name__,
            self.ieml_text,
        )
