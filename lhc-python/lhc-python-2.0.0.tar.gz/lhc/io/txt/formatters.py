class ColumnFormatter(object):
    def __init__(self, type, column, name=None):
        self.type = type
        self.column = column
        self.name = name

    def __call__(self, *parts):
        return self.type(parts[self.column])


class EntityFormatter(object):
    def __init__(self, type, entities=[], name=None):
        self.type = type
        self.entities = entities
        self.name = name

    def __call__(self, *parts):
        args = []
        kwargs = {}
        for entity, part in zip(self.entities, parts):
            if entity.name:
                kwargs[entity.name] = entity(*parts)
            else:
                args.append(entity(*parts))
        return self.type(*args, **kwargs)
