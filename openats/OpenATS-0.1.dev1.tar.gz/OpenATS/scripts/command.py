
#! coding:utf-8
"""
"""
import os
import sys
import argparse
from pathlib import Path

# -------------
# Parsing 
# -------------
parser = argparse.ArgumentParser()
parser.add_argument('--model','-m', default=None)
parser.add_argument('--setting','-s')
parser.add_argument('--test','-t', default='True', action='store_true')

if sys.argv[0] == 'python -m unittest':
    parsed_args = parser.parse_args([])
else:
    parsed_args = parser.parse_args()


RootDir = Path(os.getcwd())


def main(args=None):
    """
    No argment
    """
    print("Root Directory : {}".format(RootDir.as_posix()))
    print(parsed_args)
    

def init(args=None):
    """
    No argment
    """
    pass

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

