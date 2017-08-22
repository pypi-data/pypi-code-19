import os
from pathlib import Path, PosixPath
from datetime import datetime
import zipfile
from enum import Enum
from random import random

import yaml

# use libyaml if available (see http://pyyaml.org/ticket/34)
if hasattr(yaml, 'CLoader'):
    Loader = yaml.CLoader
else:
    Loader = yaml.Loader
if hasattr(yaml, 'CDumper'):
    Dumper = yaml.CDumper
else:
    Dumper = yaml.Dumper


class Folder(object):
    """
    Folder object based around pathlib.
    """
    def __init__(self,folder_path,):
        super(Folder, self).__init__()

        self.accepted_types = None
        self.recursive = False

        self.path = folder_path




    def __str__(self):
        return str(self.path)

    def __iter__(self):
        for x in self.files:
            yield x

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self,folder_path):
        p = Path(folder_path)
        p.resolve()
        if p.exists():

            self._path = p


        else:
            #print("Path does not exist.")
            raise FileNotFoundError
        #
        #
    @property
    def accepted_types(self):
        return self._accepted_types

    @accepted_types.setter
    def accepted_types(self,types):
        if type(types) == list or type(types) == tuple:
            pass
        elif types == None:
            pass
        else:
            raise TypeError("Only accepts list or tupples")

        self._accepted_types = types
    @property
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self,r):
        if type(r) == bool:
            pass

        else:
            raise TypeError("Only accepts True or False")

        self._recursive = r

    @property
    def files(self):
        if self.accepted_types:
            #print("updating files")
            #print(self.accepted_types)
            if self.recursive:
                files = []
                for e in self.accepted_types:
                    # recursive search for accepted from top folder
                    for f in self.path.rglob("*" + e):
                        if not f.name.startswith(".") and f.is_file():
                            files.append(f)

                return files
            else:
                # only accepted filetypes in top folder
                return [x for x in self.path.iterdir() if x.suffix in self.accepted_types]
        else:
            # all files from current folder
            return [x for x in self.path.iterdir() if x.is_file()]

    @property
    def folders(self):
        if self.recursive:
            folds = []
            for f in self.path.rglob("**"):
                if f.is_dir():
                    folds.append(f)
        else:

            folds = [x for x in self.path.iterdir() if x.is_dir()]

        return folds

    @property
    def randomFile(self):
        return self.files[int(random() * len(self.files))]

def percentOf(portion,total):
    a = portion
    b = total

    c = a / b
    d = c * 100

    return d

class AutoNumberedEnum(Enum):
    """
    Enum that is automatically numbered with increasing integers. Automatically ensures uniqueness of values.
    """

    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
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
class List2D:
    """
    Implements an 2D array with getter and setter for two indices (x,y). Based on a list but with a mapping of the
    two-dimensional indices into a one-dimensional index.
    """

    def __init__(self, dimension):
        """
        Creates an empty array with a given 2D dimension (tuple - width/height).

        :param dimension: Dimension
        """
        # create empty list
        size = dimension[0] * dimension[1]
        self._array = [0] * size
        # store dimension
        self.dimension = dimension

    def get(self, x, y):
        """
        Returns the element at position (x,y).

        :param x: x position
        :param y: y position
        :return: value
        """
        index = x + self.dimension[0] * y
        return self._array[index]

    def set(self, x, y, v):
        """
        Sets the element at position (x,y).

        :param x: x position
        :param y: y position
        :param v: value
        """
        index = x + self.dimension[0] * y
        self._array[index] = v
def index_of_element(sequence, element):
    """
    Finds the index of a certain element in a list. Returns the index of the first occurrence or ValueError if the
    element is not contained in the list. Raises a ValueError if the element is not contained in the sequence.

    Note: This is a slow operation (O(n)).

    :param sequence: iterable
    :param element: single element
    :return: the index of the element
    """
    for index, e in enumerate(sequence):
        if e == element:
            return index
    raise ValueError('element not contained in sequence')
def log_write_entry(writer, prefix, text, exception=None):
    """
    Prints a message of format: date, time, prefix, text, exception to a writer.

    :param writer:
    :param prefix:
    :param text:
    :param exception:
    """
    now = datetime.now().isoformat(' ')
    header = now + '\t' + prefix + '\t'

    print(header + text, end='\r\n', file=writer)

    if exception is not None:
        print(header + exception, end='\r\n', file=writer)




if __name__ == '__main__':

    folder = Folder('/Volumes/4TB/PROJETS/Music/WYM - Library/_scripts/tests_assets/inside/t')
    folder.accepted_types = (".mp3",".txt")
    folder.recursive = True

    f = [str(s.name) for s in folder.files]

    for i in f:
        print(i)
    # for f in folder.files:
    #     print(str(f))
    #
    # for prop in dir(folder.files[0]):
    #     print(prop)
