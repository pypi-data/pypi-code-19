class Mark(object):

    def __init__(self, type_name):
        self.type = type_name


    def to_doc(self):
        result = {
            'type': self.type
        }

        attrs = self.attrs()
        if (attrs != None):
            result['attrs'] = attrs

        return result

    def attrs(self):
        return None