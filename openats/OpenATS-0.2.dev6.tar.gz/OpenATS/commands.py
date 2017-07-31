#! coding:utf-8
"""
commands.py

"""
from __future__ import absolute_import

import os
import sys
import argparse
from pathlib import Path
from . import globalvars as g
from . import Station

# -------------
# Parsing
# -------------
parser = argparse.ArgumentParser()
parser.add_argument('--model', '-m', default=None)
parser.add_argument('--setting', '-s')
parser.add_argument('--test', '-t', default='True', action='store_true')

if sys.argv[0] == 'python -m unittest':
    parsed_args = parser.parse_args([])
else:
    parsed_args = parser.parse_args()


def init():
    """
    :usage:
        $ ats-init

    No argment
    """
    cur_dir = Path(os.getcwd())

    # Create Directories
    cur_dir.joinpath(g.DatasetDir).mkdir(exist_ok=True)
    cur_dir.joinpath(g.ModelsDir).mkdir(exist_ok=True)
    cur_dir.joinpath(g.SettingsDir).mkdir(exist_ok=True)
    cur_dir.joinpath(g.ResultsDir).mkdir(exist_ok=True)

    # Copy Stationfile
    Station.copy_default_file(to_path=cur_dir.joinpath(g.Stationfile).as_posix())


def makeDataset():
    """
    No argment
    """
    # CompleteDataset = Dataset.create(param)
    # asser CompleteDataset.success == True
    pass

def run():
    """
    --model, -m, model_001.py
    --setting, -s, 001.conf
    --test, -t, test model 
    """
    # model_py = parsed_args.model
    # setting_conf = parsed_args.setting
    # isTest = parsed_args.test
    # Stationfile = root_dir.joinpath(g.Stationfile)
    # Runner(model="model01.py", setting="01c.conf", test=False)
    pass


def runAll():
    """
    No argment
    """
    # model_dir = root_dir.joinpath(g.ModelsDir)
    # models = model_dir.glob(g.modelfile_ext)

    # conf_dir = root_dir.joinpath(g.SettingsDir)
    # settings = conf_dir.glob(g.settingfile_ext)
    pass

