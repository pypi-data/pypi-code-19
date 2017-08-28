from collections import MutableMapping
from os.path import expanduser, join
from glob import glob

from drivelink import Link


class _page(dict):
    currentDepth = 0


class Dict(Link, MutableMapping):
    """
    A dictionary class that maintains O(1) look up and write while keeping RAM usage O(1) as well.

    This is accomplished through a rudimentary (for now) hashing scheme to page the
    dictionary into parts.

    The object created can be used any way a normal dict would be used, and will
    clean itself up on python closing. This means saving all the remaining pages
    to disk. If the file_basename and file_location was used before, it will load
    the old values back into itself so that the results can be reused.

    There are two ways to initialize this object, as a standard object:

        >>> diskDict = Dict("sampledict")
        >>> for i in range(10):
        ...     diskDict[i] = chr(97+i)
        ...
        >>> diskDict[3]
        'd'
        >>> 5 in diskDict
        True
        >>> del diskDict[5]
        >>> ", ".join(str(x) for x in diskDict.keys())
        '0, 1, 2, 3, 4, 6, 7, 8, 9'
        >>> 5 in diskDict
        False

    Or through context:

        >>> with Dict("testdict") as d:
        ...     for i in range(10):
        ...         d[i] = chr(97+i)
        ...     print(d[3])
        d

    If there is a way to break dict like behavior and you can reproduce it, please
    report it to `the GitHub issues <https://github.com/cdusold/DriveLink/issues/>`_.
    """

    def __init__(self, file_basename, size_limit=1024, max_pages=16, file_location=join(expanduser("~"), ".DriveLink")):
        self.pages = _page()
        self._total = set()
        super(Dict, self).__init__(file_basename, size_limit, max_pages, file_location)

    def load_index(self):
        other_values = super(Dict, self).load_index()
        if other_values is None:
            return
        self.pages.currentDepth = other_values[0]
        for f in glob(self._file_base + '*'):
            try:
                self._total.add(int(f[len(self._file_base):]))
            except ValueError:
                pass

    def store_index(self):
        super(Dict, self).store_index(self.pages.currentDepth)

    def open_page(self, k):
        try:
            if k in self._total:
                self._load_page_from_disk(k)
        except:
            pass
        if k not in self.pages:
            self.pages[k] = _page()
            self._total.add(k)
            self.pages[k].currentDepth = self.pages.currentDepth
            self._queue.append(k)

    def determine_index(self, key):
        """
        Figures out where the key in question should be.

        Most frequently O(1), when a page becomes too large, there's
        a O(ln(n)) search that refactors O(k ln(n)) elements
        once every O(k) insertions. A full refactor usually
        happens in strides, moving a total of O(n) elements
        split up over O(ln(n)) calls. This makes the worst
        time refactor O(n) and usual refactor approximately
        O(n/ ln(n)). Average case lookup O(n/k).
        """
        k = hash(key) & self.pages.currentDepth
        i = 0
        while (k & (self.pages.currentDepth >> i)) not in self._total | set([0]):
            i += 1
        self._branchpage(k & (self.pages.currentDepth >> i))
        return k, key

    def page_indices(self):
        for k in list(self._total):
            yield k

    def __setitem__(self, key, value):
        '''
         Sets a value that a key maps to.
        '''
        super(Dict, self).__setitem__(key, value)
        i, _ = self.determine_index(key)
        if len(self.pages[i]) > self.size_limit:
            if self.pages[i].currentDepth == self.pages.currentDepth:
                self.pages.currentDepth <<= 1
                self.pages.currentDepth |= 1
            self._branchpage(i)

    def page_removed(self, number):
        self._total.remove(number)

    def __str__(self):
        return "Dictionary with values stored to " + self._file_base

    def _branchpage(self, pagenumber):
        self._guarantee_page(pagenumber)
        if self.pages[pagenumber].currentDepth == self.pages.currentDepth:
            return
        self.pages[pagenumber].currentDepth = self.pages.currentDepth
        for key in set(self.pages[pagenumber].keys()):
            k = hash(key) & self.pages.currentDepth
            if k != pagenumber:
                self._guarantee_page(pagenumber)
                v = self.pages[pagenumber][key]
                del self.pages[pagenumber][key]
                self._guarantee_page(k)
                self.pages[k][key] = v
