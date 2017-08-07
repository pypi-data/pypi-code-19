import unittest,sys
from COMTool import Main,helpAbout
import socket

class COMTest(unittest.TestCase):

    def setUp(self):
        print("setup")

    def tearDown(self):
        print("teardown")

    def test_1(self):
        print("test",sys.prefix)

        print(socket.gethostbyname(socket.gethostname()) ) # 这个得到本地ip)
        print( socket.gethostbyname_ex(socket.gethostname()))

if __name__=="__main__":
    unittest.main()

