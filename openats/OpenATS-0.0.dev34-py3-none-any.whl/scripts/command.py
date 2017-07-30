
#! coding:utf-8
"""
"""
import os
import sys

# ==================================================== #
# 1. Argment Parse
# ==================================================== #
import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('path_root_src', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        metavar=None)

def main():
    print("main!!")
    args = parser.parse_args()
    print(args)
    

def init():
    print("OpenATS.scripts.command.init")
    print("Create Directory Tree")
    print(sys.argv)

def makeDataset():
	print("OpenATS.scripts.command.makeDataset")
	print("Create Dataset")

def run():
	print("OpenATS.scripts.command.run")
	pass

def runAll():
	print("OpenATS.scripts.command.runAll")
	pass

