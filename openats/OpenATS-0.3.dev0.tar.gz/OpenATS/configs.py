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

Stationfile="""
[datasource]
path = /datasource/

[dataset]
method=1D-Signal
duration_ms=3000
"""

class Config:

    path="" #type:str

    def __init__(self, path:str):
        self.path=Path(path)

    def exists(self):
        return Path(self.path).exists()

    def get_config(self):
        if self.exists():
            import configparser
            config = configparser.ConfigParser()
            config.read(self.path.as_posix())
            return config
        else:
            raise FileNotFoundError(self.path.as_posix()+" is not found : ")
  

class Station(Config):

    @staticmethod
    def copy_default_file(to_path:str):
        
        to_path = Path(to_path)

        with open(to_path.as_posix(), "w") as fp:
            fp.write(Stationfile)

