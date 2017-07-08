"""
Utility module to support manipulation of JSON data.
"""

import json

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class JsonUtils:
    """
    Utility class containing methods for performing manipulation of JSON data.
    """

    def __init__(self):
        pass

    @staticmethod
    def convert_to_json(data_obj):
        """
        Converts supplied data object to JSON formatted string.

        :param data_obj: Data object to be converted to JSON.

        :return: The JSON formatted string.
        :rtype: str
        """

        return json.dumps(data_obj)

    @staticmethod
    def test_convert_to_json():
        """
        Test case for 'convert_to_json' method of 'JsonUtils' class.
        """

        test_dict = {"last_command_index": 2,
                     "current_command_index": 3,
                     "total_commands": 8,
                     "current_node": "10.26.45.32",
                     "input_required": "",
                     "execution_state_id": "11",
                     "rollback_initiated": "",
                     "rollback_reason": ""}

        return JsonUtils.convert_to_json(test_dict)
