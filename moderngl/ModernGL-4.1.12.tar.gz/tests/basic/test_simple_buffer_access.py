import unittest

import ModernGL


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = ModernGL.create_standalone_context()

    @classmethod
    def tearDownClass(cls):
        cls.ctx.release()

    def tearDown(self):
        self.assertEqual(self.ctx.error, 'GL_NO_ERROR')

    def test_buffer_readonly_access(self):
        buf = self.ctx.buffer(b'Hello World!')
        with buf.access(offset=1, size=4, readonly=True) as acc:
            self.assertEqual(acc.offset, 1)
            self.assertEqual(acc.size, 4)
            self.assertTrue(acc.readonly)
            self.assertEqual(acc.read(), b'ello')

    def test_buffer_readwrite_access(self):
        buf = self.ctx.buffer(b'Hello World!')
        with buf.access(offset=6, size=5, readonly=False) as acc:
            self.assertEqual(acc.offset, 6)
            self.assertEqual(acc.size, 5)
            self.assertFalse(acc.readonly)
            self.assertEqual(acc.read(), b'World')
            acc.write(b'ORLD', offset=1)
            self.assertEqual(acc.read(offset=2), b'RLD')


if __name__ == '__main__':
    unittest.main()
