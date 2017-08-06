# coding=utf-8
# modified from Trausti's implementation

from mimircache.cache.abstractCache import cache
from mimircache.cache.deprecated.OPT import alg as OPT


class Optimal(cache):
    def __init__(self, cache_size, reader):
        super().__init__(cache_size)
        reader.reset()
        self.reader = reader
        self.alg = OPT(cache_size)
        self.reqlist = []
        for e in reader:
            self.reqlist.append(e)
        self.alg.setup(self.reqlist)



    def checkElement(self, element):
        """
        :param element:
        :return: whether the given element is in the cache
        """
        return self.alg.get(element)

    def _updateElement(self, element):
        pass


    def _insertElement(self, element):
        """
        the given element is not in the cache, now insert it into cache
        :param element:
        :return: True on success, False on failure
        """
        self.alg.put(element)



    def _evictOneElement(self):
        pass



    def addElement(self, element):
        """
        :param element: the element in the reference, it can be in the cache, or not,
                        !!! Attention, for optimal, the element is a tuple of
                        (timestamp, real_request)
        :return: True if element in the cache
        """
        # if self.pq.qsize() != len(self.seenset):
        #     print("ERROR: %d: %d" % (self.pq.qsize(), len(self.seenset)))
        #     print(self.seenset)
        #     sys.exit(1)
        if self.checkElement(element):
            return True
        else:
            self._insertElement(element)
            return False

    def __repr__(self):
        return "Optimal Cache, current size: {}".\
            format(self.cache_size, super().__repr__())


