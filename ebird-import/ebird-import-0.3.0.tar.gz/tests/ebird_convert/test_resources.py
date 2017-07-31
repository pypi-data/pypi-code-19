import pkg_resources
import unittest

from ebird_import.shared import read_csv_file


def find_resource_files(files, package, resource_dir):
    """Recursively return a list of all the resources files in a directory.

    arguments:
        files (list): a list containing all the files found
        package (str): the name of the package to search
        resource_dir (str): the name of the root resource directory

    returns:
        a list of all the file found is appended to the list passed in
        the parameter, files
    """
    for file in pkg_resources.resource_listdir(package, resource_dir):
        path = "%s/%s" % (resource_dir, file)
        if pkg_resources.resource_isdir(package, path):
            find_resource_files(files, package, path)
        else:
            files.append(pkg_resources.resource_filename(package, path))


class ResourceTests(unittest.TestCase):
    """Integrity tests for the resources files."""

    def setUp(self):
        super(ResourceTests, self).setUp()
        self.files = []
        find_resource_files(self.files, 'ebird_import', '../data')

    def test_load_resources(self):
        """All the resource files can be loaded."""
        for file in self.files:
            table = read_csv_file(file)
            self.assertTrue(table)

    def test_resources_values_quotes(self):
        """Check the resource file values do not contain quotes.

        This test is used to verify that no spaces were added between entries
        and the commas separating them (in case the file was edited manually),
        otherwise the string contains the quotes used to delimit it.
        """
        for file in self.files:
            for entry in read_csv_file(file):
                self.assertTrue('"' not in ','.join(entry.values()))
