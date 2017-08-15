

class User(object):
    """Information about an authenticated user.

    Providers return different forms of information. This container is
    meant to provide a common interface with that information across all
    vendors.
    """

    ATTRIBUTES = [
        'id',
        'name',
        'nickname',
        'email',
        'avatar',
    ]

    def __getattr__(self, key):
        if key in self.ATTRIBUTES:
            return None
        raise AttributeError("The attribute \"%s\" does not exist." % key)

    def map(self, **kwargs):
        """Turns a dictionary into the properties of this user.

        Args:
            **kwargs: a dictionary of keys and values to merge into this
                instance.

        Raises:
            KeyError: Cannot map attribute "%s" to user.
        """
        for name in kwargs:
            if name not in self.ATTRIBUTES:
                raise KeyError("Cannot map attribute \"%s\" to user." % name)
            setattr(self, name, kwargs[name])

    def set_raw(self, user):
        """Saves the original data here."""
        self.user = user

    def to_dict(self):
        output = dict()
        for a in self.ATTRIBUTES:
            output[a] = getattr(self, a, None)
        return output
