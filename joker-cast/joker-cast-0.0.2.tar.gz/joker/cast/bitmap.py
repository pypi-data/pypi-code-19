#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import math
import random

import numpy


class Bitmap(object):
    def __init__(self, size, bitwidth=32, array=None, members=None):
        """
        :param size: number of bits
        :param bitwidth:
        :param array:
        :param members:
        :return:
        """
        self.size = int(math.ceil(size))
        self.bitwidth = bitwidth
        if array is None:
            dtype = 'uint{}'.format(bitwidth)
            arrsize = int(numpy.ceil(size * 1. / bitwidth))
            self.array = numpy.zeros(arrsize, dtype=dtype)
        else:
            self.array = array
        if members:
            self.update(members)

    def _verify(self, bitmap):
        if self.size != bitmap.size:
            raise ValueError('cannot use a bitmap of different size')
        if self.bitwidth != bitmap.bitwidth:
            raise ValueError('cannot use a bitmap of different bitwidth')

    def add(self, integer):
        idx = int(integer / self.bitwidth)
        self.array[idx] |= 1 << (integer % self.bitwidth)

    def __contains__(self, integer):
        idx = int(integer / self.bitwidth)
        return self.array[idx] & (1 << (integer % self.bitwidth))

    def update(self, collection):
        if isinstance(collection, Bitmap):
            self._verify(collection)
            self.array |= collection.array
            return
        for integer in collection:
            self.add(integer)

    def union(self, collction):
        this = self.copy()
        this.update(collction)
        return this

    def intersection_update(self, collection):
        if not isinstance(collection, Bitmap):
            that = self.metacopy()
            that.update(collection)
        else:
            that = collection
        self.array &= that.array

    def intersection(self, collection):
        this = self.copy()
        this.intersection_update(collection)
        return this

    def difference_update(self, collection):
        if not isinstance(collection, Bitmap):
            that = self.metacopy()
            that.update(collection)
        else:
            that = collection
        self.intersection_update(-that)

    def difference(self, collection):
        this = self.copy()
        this.difference_update(collection)
        return this

    def clear(self):
        self.array[:] = 0
        return self

    def copy(self):
        array = self.array.copy()
        return Bitmap(self.size, self.bitwidth, array=array)

    def metacopy(self):
        array = numpy.zeros_like(self.array)
        return Bitmap(self.size, self.bitwidth, array=array)

    def __neg__(self):
        array = ~ self.array
        return Bitmap(self.size, self.bitwidth, array=array)

    def __iter__(self):
        for plane in self._iter_bit_planes(False):
            for i in plane:
                yield i

    def get_members(self, count=None, random_start=False):
        members = []
        for plane in self._iter_bit_planes(random_start):
            members.extend(plane)
            if len(members) >= count:
                break
        return members

    def pick(self):
        for plane in self._iter_bit_planes(random_start=True):
            members = plane.tolist()
            if members:
                return random.choice(members)

    def _iter_bit_planes(self, random_start):
        start = random.randrange(self.bitwidth) if random_start else 0
        for j in [(i + start) % self.bitwidth for i in range(self.bitwidth)]:
            for arr in numpy.nonzero(self.array & numpy.array([1 << j])):
                # arr: indexes with bit 1 on j-th bit
                yield numpy.array([j]) + arr * self.bitwidth

    @classmethod
    def test_bitmap(cls):
        bm = cls(1001)
        items = [1, 34, 555, 90]
        for i in range(1001):
            assert i not in bm
        bm.update(items)
        for i in range(1001):
            if i in items:
                assert i in bm
            else:
                assert i not in bm
        return bm
