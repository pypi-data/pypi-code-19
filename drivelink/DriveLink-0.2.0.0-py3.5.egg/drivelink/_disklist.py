from collections import MutableSequence
from os.path import expanduser, join

from drivelink import Link


class List(Link, MutableSequence):
    """
    A list class that maintains O(k) look up and O(1) append while keeping RAM usage O(1) as well.
    Unfortunately, insert is O(n/k).

    This is accomplished through paging every size_limit consecutive values together
    behind the scenes.

    The object created can be used any way a normal list would be used, and will
    clean itself up on python closing. This means saving all the remaining pages
    to disk. If the file_basename and file_location was used before, it will load
    the old values back into itself so that the results can be reused.

    There are two ways to initialize this object, as a standard object:

        >>> diskList = List("samplelist")
        >>> for i in range(10):
        ...     diskList.append(i)
        ...
        >>> diskList[3]
        3
        >>> ", ".join(str(x) for x in diskList)
        '0, 1, 2, 3, 4, 5, 6, 7, 8, 9'
        >>> del diskList[5]
        >>> ", ".join(str(x) for x in diskList)
        '0, 1, 2, 3, 4, 6, 7, 8, 9'

    Or through context:

        >>> with List("testlist") as d:
        ...     for i in range(10):
        ...         d.append(i)
        ...     print(d[3])
        3

    If there is a way to break list like behavior and you can reproduce it, please
    report it to `the GitHub issues <https://github.com/cdusold/DriveLink/issues/>`_.
    """

    def __init__(self, file_basename, size_limit=1024, max_pages=16, file_location=join(expanduser("~"), ".DriveLink")):
        self.pages = dict()
        self._number_of_pages = 0
        super(List, self).__init__(file_basename, size_limit, max_pages, file_location)

    def load_index(self):
        other_values = super(List, self).load_index()
        if other_values is None:
            return
        self._number_of_pages = other_values[0]

    def store_index(self):
        super(List, self).store_index(self._number_of_pages)

    def open_page(self, k):
        if 0 <= k < self._number_of_pages:
            self._load_page_from_disk(k)
        else:
            raise IndexError

    def determine_index(self, key):
        """
        Figures out where the key in question should be.
        """
        if key < 0:
            key += self._length
        return divmod(key, self.size_limit)

    def page_indices(self):
        for k in range(self._number_of_pages):
            yield k

    def __delitem__(self, key):
        '''
         Deletes the key value in question from the pages.
        '''
        super(List, self).__delitem__(key)
        i, _ = self.determine_index(key)
        for i in range(i, self._number_of_pages - 1):
            self.open_page(i + 1)
            if self.pages[i + 1]:
                v = self.pages[i + 1][0]
                del self.pages[i + 1][0]
                self.pages[i].append(v)
                self._guarantee_page(i + 1)
        self._guarantee_page(self._number_of_pages - 1)
        if not self.pages[self._number_of_pages - 1]:
            del self.pages[self._number_of_pages - 1]
            self._number_of_pages -= 1

    def __reversed__(self):
        for p in reversed(range(self._number_of_pages)):
            self._guarantee_page(p)
            for i in reversed(self.pages[p]):
                yield i

    def page_removed(self, number):
        self._number_of_pages -= 1

    def __str__(self):
        return "List with values stored to " + self._file_base

    def append(self, v):
        k = self._length // self.size_limit
        if k == self._number_of_pages:
            self._newpage()
        self._guarantee_page(k)
        self.pages[k].append(v)
        self._length += 1

    def insert(self, i, v):
        k, i = divmod(i, self.size_limit)
        if k == self._number_of_pages:
            self._newpage()
        self._guarantee_page(k)
        self.pages[k].insert(i, v)
        if len(self.pages[k]) > self.size_limit:
            for k in range(k, self._number_of_pages - 1):
                self._guarantee_page(k)
                v = self.pages[k][-1]
                del self.pages[k][-1]
                self._guarantee_page(k + 1)
                self.pages[k + 1].insert(0, v)
            if len(self.pages[self._number_of_pages - 1]) > self.size_limit:
                self._newpage()
                self.pages[self._number_of_pages -
                           1].append(self.pages[self._number_of_pages - 2][-1])
                del self.pages[self._number_of_pages - 2][-1]
        self._length += 1

    def _newpage(self):
        self.pages[self._number_of_pages] = []
        self._queue.append(self._number_of_pages)
        self._number_of_pages += 1
