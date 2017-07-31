#! coding:utf-8
"""
commands.py

"""
from __future__ import absolute_import

import os
import sys
import argparse
from pathlib import Path

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


def init(args=None):
    """
    No argment
    """
    cur_dir = Path(os.getcwd())

    cur_dir.joinpath("dataset").mkdir(exist_ok=True)
    cur_dir.joinpath("models").mkdir(exist_ok=True)
    cur_dir.joinpath("settings").mkdir(exist_ok=True)
    cur_dir.joinpath("results").mkdir(exist_ok=True)

    Stationfile = cur_dir.joinpath("Stationfile")
    with Stationfile.open("w") as fp:
        fp.write("")


def makeDataset(args=None):
    """
    No argment
    """
    pass


def run(args=None):
    """
    --model, -m, model_001.py
    --setting, -s, 001.conf
    --test, -t, test model 
    """
    pass


def runAll(args=None):
    """
    No argment
    """
    pass
