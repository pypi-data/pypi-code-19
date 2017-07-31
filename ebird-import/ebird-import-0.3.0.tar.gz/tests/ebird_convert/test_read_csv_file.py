import os

from cli.test import FunctionalTest

from ebird_import.shared import FileNotFoundException, FileReadException, read_csv_file


class ReadCSVFileTests(FunctionalTest):
    """Tests for the function read_csv_file()."""

    def test_file_read(self):
        """A csv file with unix style line endings can be read"""
        csv_file = os.path.join(self._testdir, 'file.csv')
        with open(csv_file, 'wb') as fp:
            fp.write("A,B\n1,2\n".encode('utf-8'))
        result = read_csv_file(csv_file)
        self.assertEqual(result, [{ 'A': u'1', 'B': u'2'}])

    def test_file_read_dos_line_endings(self):
        """A csv file with dos line endings can be read"""
        csv_file = os.path.join(self._testdir, 'file.csv')
        with open(csv_file, 'wb') as fp:
            fp.write("A,B\r\n1,2\r\n".encode('utf-8'))
        result = read_csv_file(csv_file)
        self.assertEqual(result,  [{ 'A': u'1', 'B': u'2'}])

    def test_file_not_found(self):
        """A FileNotFoundException is raised if the file does not exist."""
        csv_file = os.path.join(self._testdir, 'file.csv')
        self.assertRaises(FileNotFoundException, read_csv_file, csv_file)

    def test_file_not_found_exception_path(self):
        """A FileNotFoundException reports the path of the missing file."""
        csv_file = os.path.join(self._testdir, 'file.csv')
        actual = ''
        try:
            read_csv_file(csv_file)
        except FileNotFoundException, err:
            actual = err.parameter
        self.assertEqual(csv_file, actual)

    def test_incorrect_encoding(self):
        """A FileReadException is raised if the file encoding is unexpected."""
        csv_file = os.path.join(self._testdir, 'file.csv')
        with open(csv_file, 'wb') as fp:
            fp.write("A,B\n1,2\n".encode('utf-16'))
        self.assertRaises(FileReadException, read_csv_file, csv_file, 'utf-8')

    def test_file_read_exception_path(self):
        """A FileReadException reports the path of the missing file."""
        csv_file = os.path.join(self._testdir, 'file.csv')
        actual = ''
        with open(csv_file, 'wb') as fp:
            fp.write("A,B\n1,2\n".encode('utf-16'))
        try:
            read_csv_file(csv_file)
        except FileReadException, err:
            actual = err.parameter
        self.assertEqual(csv_file, actual)

    def test_missing_header_column(self):
        """A FileReadException if a row has more fields than the header."""
        csv_file = os.path.join(self._testdir, 'file.csv')
        with open(csv_file, 'wb') as fp:
            fp.write("A,B\n1,2,3\n".encode('utf-8'))
        self.assertRaises(FileReadException, read_csv_file, csv_file)

    def test_missing_data_is_blank(self):
        """Blank values are added to missing data fields."""
        csv_file = os.path.join(self._testdir, 'file.csv')
        with open(csv_file, 'wb') as fp:
            fp.write("A,B,C\n1,2\n".encode('utf-8'))
        result = read_csv_file(csv_file)
        self.assertEqual(result[0]['C'], '')
