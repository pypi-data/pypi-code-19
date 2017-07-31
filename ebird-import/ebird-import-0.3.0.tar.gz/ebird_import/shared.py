import csv
import os


class CustomException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


class FileNotFoundException(CustomException):
    pass


class FileReadException(CustomException):
    pass


def read_csv_file(filepath, encoding='utf-8'):
    """Read a list of records from a CSV encoded file.

    arguments:
        filepath (str): the path to the file.

    returns:
        a list of dicts with keys for each of the columns defined in the file.
    """
    table = []

    if not os.path.exists(filepath):
        raise FileNotFoundException(filepath)

    try:
        with open(filepath, 'rb') as fp:
            reader = csv.DictReader(fp, quoting=csv.QUOTE_ALL)
            for row in reader:
                for key in row.keys():
                    if row[key] is None:
                        row[key] = ''
                    else:
                        row[key] = unicode(row[key], encoding)
                table.append(row)
    except Exception:
        raise FileReadException(filepath)

    return table
