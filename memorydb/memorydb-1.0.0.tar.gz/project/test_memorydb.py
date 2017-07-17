# -*- coding: utf-8 -*-

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

import unittest

try:
    from memorydb import MemoryDb
except:
    from .memorydb import MemoryDb

try:
    import idgen
except:
    from . import idgen

class TestApp(unittest.TestCase):
    def setUp(self):
        self.provider = MemoryDb()

    def test_simple_add_and_dumpdb(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)
        v = self.provider.dumpdb()
        self.assertEqual(v[0]['title'], item['title'])

    def test_simple_add_and_get(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)
        v = self.provider.get(scope, row_key)

    def test_simple_add_change_id_and_get(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        new_row_key = idgen.generate(__name__)

        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)
        
        p = self.provider.get(scope, row_key)
        self.provider.changeId(p, new_row_key)
        
        v = self.provider.get(scope, new_row_key)
        self.assertEqual(v['title'], item['title'])

    def test_2_adds_and_getAll(self):
        scope = idgen.generate(__name__)
        
        item1 = { "title": "hello1" }
        item2 = { "title": "hello2" }

        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, idgen.generate(__name__), item2)
        
        items = self.provider.getAll(scope)

        self.assertEqual(items[0]['title'], item1['title'])
        self.assertEqual(items[1]['title'], item2['title'])

    def test_add_get_and_update(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        
        item = { "title": "hello1" }
        
        self.provider.insert(scope, row_key, item)
        
        v = self.provider.get(scope, row_key)
        
        v['title'] = 'was updated'
        self.provider.update(v)
        
        v = self.provider.get(scope, row_key)
        
        self.assertNotEqual(v['title'], item['title'])
        self.assertEqual(v['title'], 'was updated')

    def test_3_adds_delete_and_getAll(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        
        item1 = { "title": "hello1" }
        item2 = { "title": "hello2" }
        item3 = { "title": "hello3" }
        
        self.provider.insert(scope, idgen.generate(__name__), item1),
        self.provider.insert(scope, row_key, item2),
        self.provider.insert(scope, idgen.generate(__name__), item3)
        
        self.provider.delete(scope, row_key)
        
        items = self.provider.getAll(scope)
        
        self.assertEqual(items[0]['title'], item1['title'])
        self.assertEqual(items[1]['title'], item3['title'])


if __name__ == '__main__':
    unittest.main()