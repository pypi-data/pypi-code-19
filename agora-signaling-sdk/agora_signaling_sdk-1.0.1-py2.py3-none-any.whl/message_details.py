# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


class MessageDetails(object):
    """A message class that represents detailed fields."""

    def __init__(self, msg_str):
        """
        Args:
            msg_str (str): The string typed of message.
        """
        msg_list = msg_str.split(' ', 6)
        self.msg_type = msg_list[4]
        self.msg_src = msg_list[1]
        self.msg_dst = msg_list[2]
        self.msg_flag = msg_list[3]
        self.msg_time = msg_list[5]
        self.msg_content = msg_list[6]

