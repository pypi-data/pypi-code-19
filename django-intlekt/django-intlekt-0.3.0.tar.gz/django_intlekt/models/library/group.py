from mongoengine import Document, fields


class Group(Document):
    POSITION_GAP = 2**5
    LOWEST_PREFERENCE_VALUE = 0
    HIGHEST_PREFERENCE_VALUE = -1

    name = fields.StringField(required=True, unique=True,)
    # To rank favorite groups. If null, the group is not among favorites.
    # To insert a group between other groups, just compute the mean of their
    # preferences, which avoids you to shift all indexes.
    # Cannot be zero, else inserting a group after would be impossible.
    preference = fields.FloatField(
        null=True,
        min_value=0,
        help_text="{0} refers to the lowest preference and {1} to the highest.".format(
            LOWEST_PREFERENCE_VALUE,
            HIGHEST_PREFERENCE_VALUE,
        ),
    )
    children = fields.ListField(fields.ReferenceField('USL'))

    meta = {
        'ordering': ['-preference', 'name',],
        'indexes': ['name'],
    }

    def __str__(self):
        return self.name

    @classmethod
    def match_lowest_preference_pattern(cls, p):
        return p == cls.LOWEST_PREFERENCE_VALUE

    @classmethod
    def match_highest_preference_pattern(cls, p):
        return p == cls.HIGHEST_PREFERENCE_VALUE

    @classmethod
    def get_lowest_preference(cls):
        group = cls.objects(preference__ne=None).order_by('preference').first()
        if group is None:  # There are no groups with a defined preference
            return cls.POSITION_GAP
        return group.preference / 2

    @classmethod
    def get_highest_preference(cls):
        group = cls.objects(preference__ne=None).order_by('-preference').first()
        if group is None:
            return cls.POSITION_GAP
        return group.preference + cls.POSITION_GAP
