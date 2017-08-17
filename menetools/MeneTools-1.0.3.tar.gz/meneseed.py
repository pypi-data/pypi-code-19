#!/usr/bin/python3
#-*- coding: utf-8 -*-

import argparse
import sys
import inspect
import os
from pyasp.asp import *
from menetools import utils, query, sbml

if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--net",
                        help="metabolic network in SBML format", required=True)

    args = parser.parse_args()

    draft_sbml = args.net

    print('Reading draft network from ', draft_sbml, '...', end='')
    sys.stdout.flush()
    draftnet = sbml.readSBMLnetwork(draft_sbml, 'draft')
    #print(draftnet)
    print('done.')

    print('\nSeed search ...', end='')
    sys.stdout.flush()
    model = query.get_seeds(draftnet)
    print('done.')
    quit()
