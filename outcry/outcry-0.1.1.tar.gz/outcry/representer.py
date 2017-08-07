import json
from outcry.exceptions import OutcryError, OutcryForbiddenKeyError, OutcryMissingKeyError


class Representer(object):
    def __init__(self, obj):
        self._obj = obj
        self._validated = True

    @property
    def schema(self):
        return {k: v for k, v in self.__class__.__dict__.items() if not k.startswith('_')}

    def _get_matching_value(self, name):
        return getattr(self._obj, name, None)

    @property
    def _render_keys(self):
        result = {}
        for k, v in self._obj.__dict__.items():
            if not k in self.schema.keys():
                continue
            field = self.schema[k] 
            if not field.validate(v):
                self._validated = False
            result[k] = v
        return result

    def _missing_keys(self):
        """Check if _obj is missing any fields"""
        return self.schema.keys() - self._obj.__dict__.keys()
        
    @property
    def to_json(self):
        if not self._validated:
            raise OutcryError("Outcry: Validation error, cannot convert object to JSON")
        return json.dumps(self._render_keys, default=lambda o: o.__dict__, sort_keys=True)

    def from_json(self, data):
        return self._obj(**data)
 
