import numpy
import unittest
import modconf
import ws_sheets


class CellTest(unittest.TestCase):
    def setUp(self):
        self.conf = modconf.import_conf('ws_sheets.tests.conf.simple')

    def test1(self):
        b = ws_sheets.Book(self.conf.Settings)
    
        b['0'][0, 0] = '2+2'
        self.assertEqual(b['0'][0, 0], 4)

        b['0'][0, 0] = '4'
        b['0'][0, 1] = 'sheet[0, 0]'
        self.assertEqual(b['0'][0, 1], 4)

        b['0'][0, 0] = '2'
        b['0'][0, 1] = '3'
        b['0'][0, 2] = 'sheet[0, 0:2]'
        print('cell 0,0 = ', b['0'][0, 0])
        print('cell 0,1 = ', b['0'][0, 1])
        print('cell 0,2 = ', b['0'][0, 2])
        self.assertEqual(numpy.all(b['0'][0, 2] == numpy.array([2, 3])), True)

        self.assertEqual(b.context, 0)

        b['0'][0, 0] = 'sheet[0, 0]'
        self.assertEqual(repr(b['0'][0, 0].item()), "RuntimeError('recursion',)")

        b['0'][0, 0] = ''
        self.assertEqual(b['0'][0, 0].item(), None)
    
        b['0'][0, 0] = '4'
        b['1'][0, 0] = 'book[\'0\'][0, 0]'
        self.assertEqual(b['1'][0, 0], 4)
    
    def test2(self):
        b = ws_sheets.Book(self.conf.Settings)

        b.set_cell('0', 0, 0, '1')
        b.set_cell('0', 1, 0, '2')
        b.set_cell('0', 2, 0, '3')
        b.set_cell('0', 3, 0, '4')
        b.set_cell('0', 4, 0, '5')

        b.set_cell('0', 0, 1, 'sum(sheet[0:5, 0])')

        self.assertEqual(b['0'][0, 1], 15)
       
    
