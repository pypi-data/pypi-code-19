from outcry.param import Param

class Collection(Param):
    def __init__(self, validators=None, required=False):
        super(Collection, self).__init_(validators=validators, required=required)

    def _is_collection(self, value):
        return type(value) is list and all(type(v) is dict for v in value)

    @property
    def validate(self, value):
        if self._is_collection(value):
            return all(v().validate(value) for v in self._validators)
        raise OutcryUnexpectedTypeError("Field is not a collection: {0}".format(self))


def collection(validators, required=False):
    return Collection(validators=validators, required=required)
