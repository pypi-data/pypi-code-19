import uuidreader.utils as utils
import unittest


class TestUtils(unittest.TestCase):

    def test_rfid_code_to_uuid(self):
        input = '1234567890'
        output = utils.rfid_code_to_uuid(input)
        self.assertEqual(output, 'd5cdd08d-bab5-5774-a08d-b6a71722301f')

        input = '9876543210'
        output = utils.rfid_code_to_uuid(input)
        self.assertEqual(output, 'e7208e1b-b667-5f7e-81f8-5f1d9084d4f6')

if __name__ == '__main__':
    unittest.main()