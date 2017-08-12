import subprocess
import unittest
import os
class CmdLineTestCase(unittest.TestCase):
    def setUp(self):
        try:
            res = subprocess.check_call(['python', './setup.py', 'install'], cwd=os.path.abspath('..'))
        except subprocess.CalledProcessError as e:
            print(e.output)
        self.assertEqual(res, 0)
    def test_basic_usage(self):
        res = subprocess.check_call(["doc_x_to_html", "./test_source", "./test_target"])
        self.assertEqual(res, 0)


if __name__ == "__main__":
    unittest.main()