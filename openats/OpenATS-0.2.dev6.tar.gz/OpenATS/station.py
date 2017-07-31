#! coding:utf-8
"""
station.py

"""
from __future__ import absolute_import

import os
import sys
import shutil
from pathlib import Path
from . import globalvars as g


class Station:

    def __init__(self):
        pass

    @staticmethod
    def copy_default_file(to_path:str):
        Stationfile = Path(__file__).parent \
                            .joinpath(g.ResourceDataDir) \
                            .joinpath(g.Stationfile)
        shutil.copy(Stationfile.as_posix(), to_path)

