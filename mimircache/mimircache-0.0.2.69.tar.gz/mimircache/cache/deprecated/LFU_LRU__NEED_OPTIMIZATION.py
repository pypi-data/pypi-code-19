# coding=utf-8
"""
this module gives incorrect implementation, don't use it
"""

from collections import OrderedDict

from mimircache.cache.deprecated.abstractLFU import abstractLFU


class LFU_LRU(abstractLFU):
    def __init__(self, cache_size=1000):
        super(LFU_LRU, self).__init__(cache_size)
        self.cacheDict = OrderedDict()

    def find_evict_key(self):
        evict_key = self.least_freq_elements_list.popleft()
        print(evict_key)
        return evict_key

    def _updateElement(self, element):
        super()._updateElement(element)
        self.cacheDict.move_to_end(element)
