from mongoengine import Document, fields

from .utils import USLField


class Tag(Document):
    """A word used to tag documents. Use a slug to avoid duplicates like "USA",
    "uSa", "usa", etc.
    """

    slug = fields.StringField(unique=True, required=True,)
    # The meaning can depend on the context, so a tag may have multiple usls.
    usls = fields.ListField(USLField(required=True,),)
    
    meta = {
        'ordering': ['slug'],
        'indexes': [
            'slug',
        ],
    }

    def __str__(self):
        return self.slug
