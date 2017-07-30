
#! coding:utf-8
"""
"""
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model','-m', default=None)
parser.add_argument('--setting','-s')
parser.add_argument('--test','-t', default='True', action='store_true')

if sys.argv[0] == 'python -m unittest':
    args = parser.parse_args([])
else:
    args = parser.parse_args()


def main():
    print(sys.argv)
    print(args)
    

def init():
    print(sys.argv)

def makeDataset():
    pass

def run():
    """
    --model, -m, model_001.py
    --setting, -s, 001.conf
    --test, -t, test model 
    """
    pass

def runAll():
    pass

