class MongoLocked(Exception):
    def __init__(self, obj):
        self.data = obj
        self.msg = '[MongoMixin]: locked instance is not savable.'


class MongoNotFound(Exception):
    def __init__(self, collection):
        self.msg = '[MongoMixin]: not found collection({})'.format(collection)


class MongoKeyFrozen(Exception):
    def __init__(self, collection, field_key):
        self.msg = '[MongoMixin]: {}._frozen_key({}) is immutable.'.format(collection, field_key)


class MongoKeyUndefined(Exception):
    def __init__(self, collection, field_key):
        self.msg = "[MongoMixin]: The Key({}) is undefined in {}.__fields__".format(field_key, collection)


class MongoFieldUnmovable(Exception):
    def __init__(self, collection, field_key):
        self.msg = '[MongoMixin]: The Field({}) is still in {}.__fields__ '.format(field_key, collection)
