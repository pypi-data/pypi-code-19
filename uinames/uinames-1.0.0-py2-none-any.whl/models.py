from utils import PropertyUnavailable


class People(object):
    """
    A collection of people, represented by the Person class.
    """

    def __init__(self, json=None):
        self._json = json or {}
        self.data = [Person(identity) for identity in self._json]

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "<People instance: {} Persons>".format(len(self.data))


class Person(object):
    """
    A representation of a person identity, generated from the UINames API.
    """

    def __init__(self, json=None):
        self._json = json or {}

    def __getattr__(self, item):
        try:
            obj = self._json[item]
            # determine if string or dict
            if isinstance(obj, str) or isinstance(obj, unicode):
                return obj.encode("utf-8")
            return obj
        except KeyError:
            raise PropertyUnavailable(
                "Property '{}' is does not exist or is not available for this "
                "Person.".format(item))

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "<Person instance: {} {} from {}>".format(self.name,
                                                         self.surname,
                                                         self.region)


if __name__ == "__main__":
    pass
