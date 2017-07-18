class BinaryIterator(object):
    def __init__(self, content):
        self.content = self.decode(content)

    @classmethod
    def open_file(self, path):
        return open(path, 'rb')

    def decode(self, content):
        return content

    def __iter__(self):
        return iter([self.content])
