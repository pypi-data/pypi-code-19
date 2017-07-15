import json
import os
import shutil
import zipfile

from ...exceptions import RuntimeError

def split_string(string_to_split, separator):
    """
    """
    result = string_to_split.split(separator)
    if len(result) == 1:
        return result[0], None
    return result[0], ' '.join(result[1:])


def remove_file(path):
    """
    Removes the given file if it exists, raise an error otherwise.
        @param:
            - path: string (/path/to/the/file/to/remove)

        @behave: raise an error if the specified file does not exist.
    """
    if os.path.isfile(path) == True:
        os.remove(path)
    else:
        raise RuntimeError(__name__, remove_file.__name__, "Cannot remove (" + path + "), no such file.")

def remove_directory(path):
    """
    Handler for removing a directory and all its content
        @param:
            - path: string (/path/to/the/directory/to/remove)

        @behave: raise an error if the specified directory does not exist.
    """
    if os.path.isdir(path) == True:
        shutil.rmtree(path)
    else:
        raise RuntimeError(__name__, remove_directory.__name__, "Cannot remove (" + path + "), no such directory.")

def unzip(path, destination):
    """
    Unzip the file pointed by 'path' to extract its to content to the given destination
        @params:
            - path: string (/path/to/the/file/to/unzip)
            - destination: string (/path/to/extract/the/zip)

        @behave: raise an error if either the path or the destination is invalid.
        @behave: raise an error if the archive is corrupted.
    """
    if os.path.isfile(path) == True:

        if os.path.isdir(destination) == True:
            archive = zipfile.ZipFile(path, 'r')
            result = archive.testzip()

            if result is not None:
                raise RuntimeError(__name__, unzip.__name__, "Error corrupted archive.")

            archive.extractall(destination)
            archive.close()

        else:
            raise RuntimeError(__name__, unzip.__name__, "Invalid path (" + destination + "), no such directory.")
    else:
        raise RuntimeError(__name__, unzip.__name__, "Invalid path (" + path + "), no such file.")

def load_manifest_to_dictionary(path, dictionary):
    """
    Loads the manifest.json of the plugin folder specified by 'path' to the given
    dictionary.

        @params:
            - path: string (/path/to/the/folder/containing/the/json/file)
            - dictionary: the dictionary to fill with the data.

        @behave: raise an error if the path is not pointing to a directory.
    """
    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.find(".json") > 0:
                with open(os.path.join(path, file)) as json_file:
                    data = json.load(json_file)
                for key, value in data.items():
                    dictionary[key] = value
    else:
        raise RuntimeError(__name__, parse_json_file_to_dictionary.__name__, "Invalid path (" + path + "), no such directory.")

def determine_language(path, name, dictionary, skip):
    """
    Determines in which language the plugin located at 'path' is written, and adds
    its 'name' as well as the language to the given 'dictionary'.

    For example, if the specified folder contains a plugin named 'hello_world' written
    in C++, the dictionary will look like following:

        {'hello_world': {'lang': 'cpp'}}

    @param:
        - dictionary: dictionary (the dictionary to fill)
        - path: string (path to the plugin folder)
        - name: string (the plugin name)
        - skip: array of strings  (extension to skip i.e 'json')

    """
    if os.path.isdir(path):
        for file in os.listdir(path):
            if file == 'setup.py':
                continue
            if file.find(".") > 0 and file[file.find(".") + 1:] not in skip:
                dictionary[name] = {'lang': file[file.find(".") + 1:]}


def load_plugin(path, name):
    """
    Returns a well formed dictionary built from the manifest.json found in the plugin
    folder located at 'path/name'.
    """
    dictionary = {}
    target = os.path.join(path, name)
    determine_language(target, name, dictionary, ['json', 'md', 'txt'])
    load_manifest_to_dictionary(target, dictionary[name])
    return dictionary
