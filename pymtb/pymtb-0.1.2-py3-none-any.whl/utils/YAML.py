
"""
Work in Progress not included in imports.
"""

import zipfile

import yaml


__all__ = [""]

# use libyaml if available (see http://pyyaml.org/ticket/34)
if hasattr(yaml, 'CLoader'):
    Loader = yaml.CLoader
else:
    Loader = yaml.Loader
if hasattr(yaml, 'CDumper'):
    Dumper = yaml.CDumper
else:
    Dumper = yaml.Dumper


def read_as_yaml(file_name):
    """
    Read YAML serialized Python value from file.

    :param file_name: File name
    :return: Python value
    """
    with open(file_name) as file:  # open is 'r' by default
        return yaml.load(file, Loader=Loader)


def write_as_yaml(file_name, value):
    """
    Writes Python value as YAML serialization to a file.

    :param file_name: File name.
    :param value: Python value
    """
    with open(file_name, 'w') as file:
        yaml.dump(value, file, allow_unicode=True, Dumper=Dumper)
        # TODO are keys of dictionaries in YAML sorted automatically? If not we might want to do that here.


class ZipArchiveReader:
    """
    Encapsulates a zip file and reads binary files from it, or even converts from JSON to a Python object.

    See also: https://docs.python.org/3.4/library/zipfile.html
    """

    def __init__(self, file):
        """
        Opens the zip file in read-only mode.

        :param file: File name
        """
        self.zip = zipfile.ZipFile(file)  # mode is 'r' by default

    def read(self, name):
        """
        Reads the file name from the zip archive.

        :param name: File name.
        :return: byte array
        """
        return self.zip.read(name)

    def read_as_yaml(self, name):
        """
        Reads the file name from the zip archive and interprets the byte array as UTF-8 YAML.

        :param name: File name.
        :return: De-serialized Python value.
        """
        data = self.read(name)
        obj = yaml.load(data.decode(), Loader=Loader)
        return obj

    def __del__(self):
        """
        Closes the zip upon deletion.
        """
        self.zip.close()


class ZipArchiveWriter:
    """
    Encapsulates a zip file to write files into it or even whole Python objects via YAML.

    See also: https://docs.python.org/3.4/library/zipfile.html
    """

    def __init__(self, file):
        """
        Open the zip file in write mode with standard zlib compression mode.

        :param file: File name
        """
        self.zip = zipfile.ZipFile(file, mode='w', compression=zipfile.ZIP_DEFLATED)

    def write(self, name, data):
        """
        Writes a byte array to a file in the archive.

        :param name: File name
        :param data: byte array
        """
        self.zip.writestr(name, data)

    def write_as_yaml(self, name, obj):
        """
        Writes a Python value as UTF-8 YAML into a file in the archive.

        :param name: File name
        :param obj: Python value
        """
        data = yaml.dump(obj, allow_unicode=True, Dumper=Dumper).encode()
        self.write(name, data)

    def __del__(self):
        """
        Closes the zip upon deletion.
        """
        self.zip.close()