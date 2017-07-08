class Property(object):
    def __init__(self, validators=None, required=False):
        self._validators = validators
        self._required = required

    def validate(self, value):
        if not self._validators:
            return True
        return all(v().validate(value) for v in self._validators)

    @property
    def required(self):
        return self._required
       

class Collection(Property):
    pass


class Field(Property):
    pass


def field(validators=None, required=False):
    return Field(validators=validators, required=required)

