# -*- coding: utf-8 -*-

import unittest

from StringIO import StringIO

from ebird_import.handlers import WorldbirdsHandler


class ReadHeaderTests(unittest.TestCase):
    """Tests for the function read_header()."""

    def setUp(self):
        super(ReadHeaderTests, self).setUp()
        self.obj = WorldbirdsHandler()

    def test_load_file_with_bom(self):
        """Find headers when file contents has a UTF-16 byte order mark."""
        contents = StringIO(u"""\xfe\xffThese data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

Data
	Family name	Family sequence	Species sequence	Scientific name
1	Procellariidae	18	6900	Puffinus mauretanicus
        """)
        result = self.obj.read_header(contents)
        self.assertTrue(result)

    def test_load_file_without_bom(self):
        """Find headers when UTF-16 byte order mark is missing."""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

Data
	Family name	Family sequence	Species sequence	Scientific name
1	Procellariidae	18	6900	Puffinus mauretanicus
        """)
        result = self.obj.read_header(contents)
        self.assertTrue(result)

    def test_load_file_with_dos_line_endings(self):
        """Find headers when UTF-16 byte order mark is missing."""
        contents = StringIO(u"""These data have been extracted.\r
\r
Search conditions used\r
Purpose	Species	Region/State	Location	Start date	End date\r
\r
\r
Total no. records	1\r
\r
Data\r
	Family name	Family sequence	Species sequence	Scientific name\r
1	Procellariidae	18	6900	Puffinus mauretanicus\r
        """)
        result = self.obj.read_header(contents)
        self.assertTrue(result)

    def test_load_file_without_data_section(self):
        """An exception is raised when data section is missing."""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1
        """)
        self.assertRaises(ValueError, self.obj.read_header, contents)

    def test_load_file_with_empty_data_section(self):
        """An exception is raised when data section is empty."""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

Data
        """)
        self.assertRaises(ValueError, self.obj.read_header, contents)

    def test_load_file_with_truncated_data_section(self):
        """Function completes when records are missing."""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

Data
	Family name	Family sequence	Species sequence	Scientific name
        """)
        result = self.obj.read_header(contents)
        self.assertTrue(result)

    def test_load_file_with_missing_headers(self):
        """An exception is raised when headers are missing."""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

Data
1	Procellariidae	18	6900	Puffinus mauretanicus
        """)
        self.assertRaises(ValueError, self.obj.read_header, contents)

    def test_data_with_whitespace(self):
        """Find headers when data section has extra whitespace"""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

    Data
	Family name	Family sequence	Species sequence	Scientific name
1	Procellariidae	18	6900	Puffinus mauretanicus
        """)
        result = self.obj.read_header(contents)
        self.assertTrue(result)

    def test_data_lowercase(self):
        """Find headers when data section is lower case"""
        contents = StringIO(u"""These data have been extracted.

Search conditions used
Purpose	Species	Region/State	Location	Start date	End date


Total no. records	1

data
	Family name	Family sequence	Species sequence	Scientific name
1	Procellariidae	18	6900	Puffinus mauretanicus
        """)
        result = self.obj.read_header(contents)
        self.assertTrue(result)
