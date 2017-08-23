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
    parser.add_argument("-o", "--output",
                        help="metabolic network in lp format", required=True)

    args = parser.parse_args()

    draft_sbml = args.net
    output_lp = args.output

    print('Reading draft network from ', draft_sbml, '...', end='')
    sys.stdout.flush()
    draftnet = sbml.readSBMLnetwork(draft_sbml, 'draft')
    #print(draftnet)
    print('done.')

    print('\nExport to ', output_lp)
    sys.stdout.flush()
    draftnet.to_file(output_lp)
    print('done.')
    quit()
