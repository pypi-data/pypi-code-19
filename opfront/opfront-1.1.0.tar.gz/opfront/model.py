class Model(object):

    """
    Model represents a single resource instance (Ex: a specific Store)

    Args:
        resource (OpfrontResource): Resource that instantiated this model
        **attrs (dict): Attributes of the model
    """

    def __init__(self, resource, **attrs):
        self._res = resource
        self._excluded_keys = dir(self)

        for attr_name, attr_value in attrs.items():
            setattr(self, attr_name, attr_value)

    def save(self):
        """
        Creates or updates the model

        Returns:
            Model: Updated model (with generated ID, if applicable)

        """
        if hasattr(self, 'id') and self._res.exists(self.id):
            # Update
            return self._res.update(self)

        # Create
        return self._res.create(self)

    def delete(self):
        """
        Deletes the model
        """
        if hasattr(self, 'id'):
            self._res.delete(self.id)
        else:
            pass

    @property
    def serialized(self):
        serialized_dict = {}

        for k in dir(self):
            if k in self._excluded_keys or k.startswith('_'):
                continue

            val = getattr(self, k)
            if isinstance(val, Model):
                k = k + '_id'
                val = val.id

            elif isinstance(val, list) and all([isinstance(x, Model) for x in val]):
                k = k.rstrip('s') + '_ids'
                val = [x.id for x in val]

            serialized_dict[k] = val

        return serialized_dict
