"""
Utility module to manipulate files.
"""

import os
import csv
import types
import shutil
import datetime

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class FileUtils:
    """
    Utility class containing methods to manipulate files.
    """

    def __init__(self):
        pass

    @staticmethod
    def check_file_exists(file_path):
        """
        Checks if the given path points to a file or not.

        :param file_path: The full path of the file to be verified.

        :return: True, is specified path points to a file, False otherwise.
        :rtype: bool
        """

        if os.path.isfile(file_path):
            return True

        return False

    @staticmethod
    def get_file_extension(file_path):
        """
        Gets extension of the file at the specified path.

        :param file_path: The full path of the file whose extension is to be extracted.

        :return: The file extension.
        :rtype: str
        """

        return os.path.splitext(file_path)[1]

    @staticmethod
    def read_file(file_path):
        """
        Reads a file from the specified path and returns list containing its lines.

        :param file_path: The full path of the file to be read.

        :return: List representing each line of the file.
        :rtype: list
        """

        try:
            file_handler = open(file_path, "r")
            file_data = file_handler.readlines()
            file_handler.close()

            return file_data
        except Exception as ex:
            pass

    @staticmethod
    def get_file_last_line(file_path):
        """
        Returns the last line of the specified file.

        :param file_path: The full path of the file to be read.

        :return: The last of the file. False in case empty/non-existent file is encountered.
        :rtype: str
        """

        if FileUtils.check_file_exists(file_path):
            if FileUtils.get_file_metadata(file_path)["FILE_SIZE"] > 0:
                file_lines = FileUtils.read_file(file_path)

                return file_lines[len(file_lines)-1]

        return False

    @staticmethod
    def write_to_file(file_path, data, write_mode="a"):
        """
        Writes supplied data to file at specified path.

        :param file_path: The full path of the file where data is to be written.
        :param data: The data to be written into the file.
        :param write_mode: The file write mode: w->Create new file, a->Append to existing file.
                           The default write mode is 'append'.

        :return: True, if file write was successful, False otherwise.
        :rtype: bool
        """

        try:
            file_path = os.path.normpath(file_path)
            file_handle = open(file_path, write_mode)
            file_handle.write(data)
            file_handle.close()

            return True
        except IOError as ex:
            return False

    @staticmethod
    def create_file_name_string(name_components, extension, separator="_"):
        """
        Combines multiple components provided in a list with a file extension string to create a complete file name.

        Main use is to keep the actual code clutter-free.

        :param name_components: List of components to be part of the final file name.
        :param extension: Extension of the file.
        :param separator: Separator to be used for isolating name components.

        :return: The final file name string, if name_components is a valid list, False otherwise.
        :rtype: str
        """

        if isinstance(name_components, types.ListType):
            if len(name_components) > 0:
                name_string = ""

                for component in name_components:
                    name_string += component + separator

                name_string = name_string[:-1]
                name_string += extension

                return name_string

        return False

    @staticmethod
    def copy_file(src_path, dest_path):
        """
        Copies a file from supplied source to destination path.

        :param src_path: The full path of the file source.
        :param dest_path: The full path of the file destination.

        :return: True, if copy was successful, False otherwise.
        :rtype: bool
        """

        try:
            shutil.copy(src_path, dest_path)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def load_csv(csv_file_path):
        """
        Reads a CSV file and returns a list of rows, each containing header-value pairs.

        :param csv_file_path: The full path of the CSV file.

        :return: The list of CSV rows, as header-value pair dictionaries, False in case of Exception.
        :rtype: list
        """

        try:
            csv_reader = csv.DictReader(open(csv_file_path))

            return csv_reader
        except Exception as ex:
            return False

    @staticmethod
    def get_file_metadata(file_path, size_unit="k", time_format="%Y-%m-%d %I:%M:%S"):
        """
        Returns file meta-data containing,
         - Last modified time
         - File size
         - File name
         - File directory

        :param file_path: The full path of the file to be analyzed.
        :param size_unit: Units in which to report file size.
        :param time_format: Format in which to report file modification time.

        :return: Dictionary containing relevant file meta data.
        :rtype: dict
        """

        last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime(time_format)

        # get file size in bytes
        file_size = os.path.getsize(file_path)
        base_unit = 1024.0
        decimal_limit = 2

        if size_unit == "b":
            pass
        elif size_unit == "k":
            file_size /= base_unit
        elif size_unit == "m":
            file_size = (file_size / base_unit) / base_unit
        elif size_unit == "g":
            file_size = ((file_size / base_unit) / base_unit) / base_unit

        # limit floating-point value to X decimal points
        if size_unit != "b":
            file_size = round(file_size, decimal_limit)

        return {"FILE_LAST_MODIFIED": str(last_modified_time),
                "FILE_SIZE": str(file_size),
                "FILE_NAME": str(os.path.basename(file_path)),
                "FILE_DIRECTORY": str(os.path.dirname(file_path))}
