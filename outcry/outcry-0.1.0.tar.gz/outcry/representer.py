import json
from outcry.exceptions import OutcryError, OutcryForbiddenKeyError, OutcryMissingKeyError


class Representer(object):
    def __init__(self, obj):
        self._obj = obj
        self._validated = False
        self.validate()

    @property
    def schema(self):
        return {k: v for k, v in self.__class__.__dict__.items() if not k.startswith('_')}

    @property
    def validated(self):
        return self._validated
    
    def validate(self):
        if not self._has_invalid_keys and self._validations_pass:
            self._validated = True

    @property
    def _has_invalid_keys(self):
        if len(self._invalid_keys) > 0:
            raise OutcryForbiddenKeyError("Keys are notdefined in schema {0}".format(self._invalid_keys)) 
        if len(self._required_keys) > 0:
            raise OutcryMissingKeyError("The following keys are required {0}".format(self._required_keys))
        return False

    def _get_matching_value(self, name):
        return getattr(self._obj, name, None)

    @property
    def _validations_pass(self):
        return all(f.validate(self._get_matching_value(p)) for p, f in self.schema.items())

    @property
    def _invalid_keys(self):
        """Check if obj has any non-declared attributes"""
        return self._obj.__dict__.keys() - self.schema.keys()
    
    @property
    def _required_keys(self):
        required_keys = [k for k, f in self.schema.items() if f.required]
        return required_keys - self._obj.__dict__.keys()

    @property
    def _missing_keys(self):
        """Check if obj is missing any required keys"""
        return self._required_keys - self.schema.keys()
        
    @property
    def to_json(self):
        if not self._validated:
            raise OutcryError("Outcry: Validation error, cannot convert object to JSON")
        return json.dumps(self._obj, default=lambda o: o.__dict__, sort_keys=True)

    def from_json(self, data):
        return self._obj(**data)
 
