"""
Utility module to manipulate excel spreadsheets.
"""

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class ExcelUtils:
    """
    Utility class containing methods for manipulating excel spreadsheets.
    """

    def __init__(self):
        self.excel_type_validation_map = {
            "xls": {"signature": b'\x50\x4B\x05\06',
                    "seek_start_position": 0,
                    "seek_offset": 512,
                    "byte_capture_size": 8},
            "xlsx": {"signature": b'\x09\x08\x10\x00\x00\x06\x05\x00',
                     "seek_start_position": 2,
                     "seek_offset": -22,
                     "byte_capture_size": 4}
        }

    def detect_excel_type(self, file_path, detection_mode=0):
        """
        Detects the type of excel spreadsheet supplied.

        :param file_path: The full path of the spreadsheet file to be analyzed.
        :param detection_mode: Type of detection method to use,
                               0 - Simple detection (fast and not always accurate)
                               1 - Slower but 100% accurate

        :return: The detected spreadsheet type, False if no valid type was found.
        :rtype: str
        """

        if detection_mode == 0:
            import os
            file_name, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.split(".")[1]

            if file_extension in self.excel_type_validation_map.keys():
                return file_extension
        elif detection_mode == 1:
            for spreadsheet_type, validation_map in self.excel_type_validation_map.iteritems():
                with open(file_path, "rb") as fh:
                    fh.seek(validation_map["seek_offset"], validation_map["seek_start_position"])
                    file_bytes = fh.read(validation_map["byte_capture_size"])

                    # print codecs.getencoder('hex')(file_bytes)

                    if file_bytes == validation_map["signature"]:
                        return spreadsheet_type

        return False
