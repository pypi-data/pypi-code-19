import unittest
import mock

import sys
from contextlib import contextmanager
from StringIO import StringIO

from datetime import datetime

from check_talend_job import check_talend_job
from check_talend_job import config


@contextmanager
def captured_output():
    """ A context manager to capture output """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class Test__get_time(unittest.TestCase):
    def test__good_format(self):
        time = datetime(1900,1,1,12,12,12)
        self.assertEqual(check_talend_job.get_time("string 12:12:12;string string"), time)

    def test__bad_time(self):
        with self.assertRaises(ValueError):
            check_talend_job.get_time("string 12:12:61;string string")

    def test__bad_format(self):
        with self.assertRaises(Exception):
            check_talend_job.get_time("12:12:12")


class Test__check_log_file(unittest.TestCase):

    def mock_check_log_file(self, list_lines):
        config.endingString = ";END\n"
        mopen = mock.mock_open(read_data=list_lines)
        with mock.patch('check_talend_job.check_talend_job.open', mopen, create=True):
            return check_talend_job.check_log_file("/dev/null")


    def test__ok_file(self):
        ok_file = "".join(["String 10:10:10;string string\n",
                          "String 10:10:10;string string\n",
                          "String 10:10:11;END\n",
                          "\n"])
        ok_return = "OK: task run in 1s | time=1.0", 0

        self.assertEqual(self.mock_check_log_file(ok_file), ok_return)

    def test__critical_file(self):
        critical_file = "".join(["String 10:10:10;string string\n",
                          "String 10:10:10;string string\n",
                          "String 10:10:11;Exception string\n",
                          "\n"])
        critical_return = 'CRITICAL: String 10:10:11;Exception string | time=1.0', 2

        self.assertEqual(self.mock_check_log_file(critical_file), critical_return)

    def test__file_not_found(self):
        self.assertEqual(check_talend_job.check_log_file(''), ('UNKNOWN: File  not found', 3))

    def test__too_few_line(self):
        too_short_file = "String 10:10:10;string string\n"
        self.assertEqual(self.mock_check_log_file(too_short_file), ('UNKNOWN: Not a talend log file', 3))

    def test__bad_file_format(self):
        bad_file = "String"
        bad_result = "UNKNOWN: Wrong format for line of log file", 3
        self.assertEqual(self.mock_check_log_file(bad_file), bad_result)


class Test__main(unittest.TestCase):
    message = "message"

    @mock.patch("check_talend_job.check_talend_job.get_latest_job")
    @mock.patch("check_talend_job.check_talend_job.parse_args")
    @mock.patch("check_talend_job.check_talend_job.check_log_file")
    def test_output(self, check_log_file, parse_args, get_latest_job):
        check_log_file.return_value = self.message, 0
        args = mock.MagicMock()
        args.job = None
        parse_args.return_value = args
        get_latest_job.return_value = None
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit) as exitException:
                check_talend_job.main()
        output = out.getvalue().strip()
        self.assertEqual(output, self.message)
        self.assertEqual(exitException.exception.code, 0)
