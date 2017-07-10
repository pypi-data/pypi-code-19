#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius_save_stock_prices                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program saves Google Finance stock prices to CSV.                       #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help              display help message
    --version               display version and exit

    --instruments=TEXT      comma-separated instruments list to save (none for
                            default list)          [default: none]
    --filenameout=FILENAME  filename of output CSV [default: stocks.csv]
"""

import docopt
import io
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

import denarius
import pandas as pd

name    = "denarius_save_stock_prices"
version = "2017-06-13T1539Z"
logo    = None

def main(options):

    instruments = options["--instruments"]
    if instruments == "none":
        instruments = [
            "AAPL",
            "GOOGL",
            "GOOG",
            "MSFT",
            #"FB",
            "ORCL",
            #"TSM",
            "INTC",
            "CSCO",
            #"IBM",
            #"SAP",
            "AVGO",
            #"DCM",
            "NVDA",
            "QCOM"
        ]
    else:
        instruments = instruments.split(",")
    filename_out = options["--filenameout"]

    dfs = []
    for instrument in instruments:
        dfs.append(denarius.instrument_DataFrame(instrument = instrument))
    df = denarius.merge_instrument_DataFrames(dfs = dfs)
    df.to_csv(filename_out)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
