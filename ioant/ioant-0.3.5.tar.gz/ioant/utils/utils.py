import os
import sys
import platform
import json
import socket
import fcntl
import struct


def open_file_as_string(filepath):
    with open(filepath, 'r') as ftemp:
        templateString = ftemp.read()
    return templateString


def return_absolut_path(script_path, relative_path):
    return os.path.realpath(os.path.join(script_path, relative_path))


def fetch_json_file_as_dict(path_to_json):
    json_str = open_file_as_string(path_to_json)
    return json_string_to_dict(json_str)


def json_string_to_dict(json_string):
    json_dict = json.loads(json_string)
    return json_dict


def topic_to_dict(topic):
    sub_topics_list = topic.split('/')
    if len(sub_topics_list) is not 6:
        return None
    else:
        topic_dict = {}
        topic_dict['top'] = sub_topics_list[0]
        topic_dict['global'] = sub_topics_list[1]
        topic_dict['local'] = sub_topics_list[2]
        topic_dict['client_id'] = sub_topics_list[3]
        topic_dict['message_type'] = int(sub_topics_list[4])
        topic_dict['stream_index'] = int(sub_topics_list[5])
        return topic_dict


def determine_os_and_arch():
    os_system = platform.system().lower()
    os_arch = platform.machine().lower()

    return (os_system, os_arch)

if __name__ == '__main__':
    unittest.main()
