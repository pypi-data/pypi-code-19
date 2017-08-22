import unittest

import ModernGL


class TestBuffer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = ModernGL.create_standalone_context()

    @classmethod
    def tearDownClass(cls):
        cls.ctx.release()

    def tearDown(self):
        self.assertEqual(self.ctx.error, 'GL_NO_ERROR')

    def test_1(self):
        buf1 = self.ctx.buffer(data=b'\xAA\x55' * 10)
        buf2 = self.ctx.buffer(reserve=buf1.size)
        buf2.write(b'Hello World!')

        self.assertEqual(buf1.read(5, offset=1), b'\x55\xaa\x55\xaa\x55')
        self.assertEqual(buf2.read(5, offset=6), b'World')

        self.ctx.copy_buffer(buf2, buf1, read_offset=1, write_offset=6, size=5)
        self.assertEqual(buf2.read(12), b'Hello \x55\xaa\x55\xaa\x55!')


if __name__ == '__main__':
    unittest.main()
