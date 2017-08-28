from collections import MutableMapping
from os.path import expanduser, join
from glob import glob

from drivelink import Link


class OrderedDict(Link, MutableMapping):
    """
    A dictionary class that maintains O(1) look up and write while keeping RAM usage O(1) as well.

    This is accomplished through a rudimentary (for now) hashing scheme to page the
    dictionary into parts.
    """

    def __init__(self, file_basename, size_limit=1024, max_pages=16, file_location=join(expanduser("~"), ".DriveLink")):
        self.pages = {}
        self._total = set()
        super(OrderedDict, self).__init__(file_basename, size_limit, max_pages, file_location)

    def load_index(self):
        other_values = super(OrderedDict, self).load_index()
        if other_values is None:
            return
        for f in glob(self._file_base + '*'):
            try:
                self._total.add(int(f[len(self._file_base):]))
            except ValueError:
                pass

    def open_page(self, k):
        try:
            if k in self._total:
                self._load_page_from_disk(k)
        except:
            pass
        if k not in self.pages:
            self.pages[k] = {}
            self._total.add(k)
            self._queue.append(k)

    def determine_index(self, key):
        """
        Figures out where the key in question should be.
        """
        # TODO: Refactor into b-tree
        k = hash(key) // self.size_limit
        return k, key

    def page_indices(self):
        for k in list(self._total):
            yield k

    def page_removed(self, number):
        self._total.remove(number)

    def __str__(self):
        return "Dictionary with values stored to " + self._file_base
