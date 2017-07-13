#!/usr/bin/env python3
# System modules
import json

# External modules

# Internal modules


# Variables
EMPTY_JSON = {}

# read json from a filename
def read_json_from_file(filename):
    """
    read json from a file given then filename
    args:
        filename (str): The path to the file to read
    returns:
        dict, empty dict if error occured during read
    """
    try: # open and read, return result
        with open(filename, "r") as f:
            return json.load(f)
    except: # didn't work, return empty dict
        return {}

# write json to file
def write_json_to_file(data, filename):
    """
    write data to json file
    args:
        filename (str): the json file to write the data to
        data (dict): the data to write to the file
    returns:
        True on success, False otherwise
    """
    try:
        jsonstr = json.dumps(data,sort_keys=True,indent=4) # try to convert
        # write to file
        with open(filename, "w") as f: f.write(jsonstr)
        return True
    except:
        return False

# do nothing
def nothing(): # pragma: no cover
    pass
