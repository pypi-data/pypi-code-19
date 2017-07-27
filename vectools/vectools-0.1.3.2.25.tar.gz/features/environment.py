import argparse
import sys
import os


def before_scenario(context, scenario):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    context.parser = parser
    context.sys = sys.argv[:]
    context.tmp_files = []


def after_scenario(context, scenario):
    sys.argv = context.sys[:]
    for f in context.tmp_files:
        os.unlink(f)
