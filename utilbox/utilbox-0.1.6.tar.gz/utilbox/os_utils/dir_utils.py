"""
Utility module to manipulate directories.
"""

import os
import types
import shutil

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class DirUtils:
    """
    Utility class containing methods to manipulate directories.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_dir(dir_path):
        """
        Creates a directory at the specified path.

        :param dir_path: The full path of the directory to be created.

        :return: True, if directory was created, False otherwise.
        :rtype: bool
        """

        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                return True

            return False
        except Exception as ex:
            return False

    @staticmethod
    def create_dir_path_string(path_components, separator="/"):
        """
        Combines list of supplied path components to create a full directory path.

        Main use is to keep the actual code clutter-free.

        :param path_components: List of components to be part of the final directory path.
        :param separator: Separator to be used for isolating directory path components.

        :return: The full directory path string, if path_components is a valid list, False otherwise.
        :rtype: str
        """

        if isinstance(path_components, types.ListType):
            if len(path_components) > 0:
                path_string = ""

                for component in path_components:
                    path_string += component + separator

                path_string = path_string[:-1]
                path_string = os.path.normpath(path_string)

                return path_string

        return False

    @staticmethod
    def fix_path(path1, path2):
        """
        Combines 2 given paths to form OS compliant path with correct path separators.

        Example:
            1st path (Linux): /root/some_dir; 2nd path (Windows): \test\data
            After combining the above paths,
                On Windows: \root\some_dir\test\data
                On Linux: /root/some_dir/test/data

        :param path1: The first path to be combined.
        :param path2: The second path to be combined.

        :return: The final combined path.
        :rtype: str
        """

        return os.path.normpath(path1 + path2)

    @staticmethod
    def check_valid_dir(dir_path):
        """
        Verifies if given directory path exists and is a valid directory.

        :param dir_path: The full path of the directory to be verified.

        :return: True if path contains a valid directory, False otherwise.
        :rtype: bool
        """

        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                return True

        return False

    @staticmethod
    def create_archive(output_file_name, source_path, archive_format="zip"):
        """
        Creates a compressed archive of the specified directory.

        :param output_file_name: Name of the output archive file.
        :param source_path: The full path of the source to be archived.
        :param archive_format: The format to be used for archiving, and can be either ZIP, TAR, BZTAR or GZTAR.

        :return: True if archiving was successful, False otherwise.
        :rtype: bool
        """

        if shutil.make_archive(output_file_name, archive_format.lower(), source_path):
            return True

        return False
