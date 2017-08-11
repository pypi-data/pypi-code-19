import CommandParser
import unittest

class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser.CommandParser()

    # aws-sudo -m 123 testProfile command -m 321
    def test_in_place(self):

        t = ['-m', '123', 'testProfile', 'command', '-m', '321']
        args = self.parser.get_arguments(t)

        self.assertEqual(args.profile, 'testProfile')
        self.assertEqual(args.mfa_code, '123')
        self.assertEqual(args.command, ['command', '-m', '321'])


if __name__ == '__main__':
    unittest.main()
