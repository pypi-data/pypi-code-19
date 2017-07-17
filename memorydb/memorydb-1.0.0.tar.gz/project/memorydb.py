# MIT License
# Copyright (c) 2017 David Betz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from time import time
import copy

class MemoryDb():
    def __init__(self):
        self.table = []

    def resetDatabase(self):
        self.table = []

    def dumpdb(self, *args):
        if len(args) == 0:
            return self.table[:]

        return args(self.table[:])

    def delete(self, partition_key, row_key):
        self.table = [v for v in self.table if v['partition_key'] != partition_key or v['row_key'] != row_key]

    def insert(self, partition_key, row_key, item):
        item['partition_key'] = partition_key
        item['row_key'] = row_key
        item['timestamp'] = time()
        self.table.append(copy.copy(item))

    def get(self, partition_key, row_key):
        items = [v for v in self.table if v['partition_key'] == partition_key and v['row_key'] == row_key]
        if len(items) > 0:
            return items[0]
        else:
            raise ValueError(404)

    def getAll(self, partition_key):
        return sorted([v for v in self.table if v['partition_key'] == partition_key], key=lambda k: k['timestamp']) 

    def changeId(self, item, new_id):
        if 'partition_key' not in item:
            raise ValueError('item.partition_key is required')

        if 'row_key' not in item:
            raise ValueError('item.row_key is required')

        self.delete(item['partition_key'], item['row_key'])

        item['row_key'] = new_id

        self.table.append(item)

    def update(self, item):
        if 'partition_key' not in item:
            raise ValueError('item.partition_key is required')

        if 'row_key' not in item:
            raise ValueError('item.row_key is required')

        self.delete(item['partition_key'], item['row_key'])

        self.table.append(item)