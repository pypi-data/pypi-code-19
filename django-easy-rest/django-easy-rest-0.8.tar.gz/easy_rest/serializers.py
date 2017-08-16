class FullDebuggerSerializer(object):
    def __init__(self):
        self.message = "this is used for debugging don't use this serializer for other fields for security reasons !."

    def serialize(self, model):
        data = model.__dict__
        for field in data:
            if 'django.db' in str(type(data[field])):
                data[field] = self.serialize(data[field])
        return data
