import os
import json
from . import _config
import shutil


def open_extra_data_files(datafiles):
    extra_data = {}
    for filename in datafiles:
        with open(filename, 'r') as f:
            extra_data[os.path.splitext(os.path.basename(filename))[0]] = json.load(f)

    return extra_data


def clear():
    shutil.rmtree(_config.BASE_PATH)
