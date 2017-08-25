class BinaryIterator(object):
    def __init__(self, content):
        self.content = self.decode(content)
        self._stop = False

    @classmethod
    def open_file(self, path):
        return open(path, 'rb')

    def decode(self, content):
        return content

    def __next__(self):
        if self._stop:
            raise StopIteration
        else:
            self._stop = True
            return self.content
