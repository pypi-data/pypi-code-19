class Surjection(dict):
    def __init__(self, mapping=None, **kwargs):
        if isinstance(mapping, dict):
            dup = []
            for val in mapping.values():
                if val in dup:
                    raise ValueError('Values must be unique')
                else:
                    dup.append(val)
            self.reverse = {key: val for key in mapping.values() for val in mapping.keys()}
            super().__init__(mapping, **kwargs)
        elif hasattr(mapping, '__iter__'):
            dup = []
            for item in mapping:
                if item[1] in dup:
                    raise ValueError('Values must be unique')
                else:
                    dup.append(item[1])
            rev_mapping = [(item[1], item[0]) for item in mapping]
            self.reverse = dict(rev_mapping)
            super().__init__(mapping, **kwargs)
        else:
            self.reverse = {}
            super().__init__()

    def __setitem__(self, key, value):
        if value in self.reverse.keys():
            raise ValueError('Values must be unique')
        try:
            self.reverse[value] = key
        except TypeError:
            raise TypeError('Unhashable type {}'.format(type(value)))
        else:
            super().__setitem__(key, value)
