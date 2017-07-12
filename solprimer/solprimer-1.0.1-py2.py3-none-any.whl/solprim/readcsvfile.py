"""
solprim_readcsvfile.py
=====
Python function to read csv data into pandas dataframe

developed with Python3.5, tested with Python2.7

call package with 'import solprim_pckg.readcsvfile as csv'

functions included
    - readcsvfile(filename)


'solprimer' Python Solar Energy Calculation Primer
Copyright (C) 2017 by Gianguido Piani
contact information : <solarprimer@mailbox.org>

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

For a full copy of the GNU General Public License see 
<http://www.gnu.org/licenses/>.

"""
# ===== ensure backward compatibility with Python2.7
from __future__ import division



import pandas as pd

def readcsvfile(filename):

    """
    read a csv file and return a pandas dataframe with all parameters
    accessible in structured form

    function to be used with the component libraries in csv format
    delivered together with the SAM system :
    - CEC_Inverters.csv [14 x 3772]
    - CEC_Modules.csv [21 x 13953]
    - Sandia_Modules [42x523]
    - SRCC_Collectors.csv [8x437]

    input
    - filename with path accessible from the current work directory

    Important Notice =====
    The System Advisory Model (SAM) software has been developed by NREL
    For copyright and other information see https://sam.nrel.gov/

    """

    # read csv data into a pandas dataframe
    # the first column [index=0] is assumed to be the index (it contains
    # the names of the components)
    # the first row [row=0] is header for the data content
    # rows 1, 2 contain extra information for the header bur are not
    # relevant for the data content

    df = pd.read_csv(filename, index_col=0, skiprows=[1,2])

    # the column names are read from row=0 in the csv file
    colnames = df.columns.values.tolist()

    # check for blanks in the column names, replace with underscore '_'
    # build a list with the new column names, assign the list to dataframe
    
    parsedcolnames = []
    for colname in colnames:
        parsedcolnames.append(colname.replace(' ', '_'))

    df.columns = parsedcolnames

    # check for blanks or other non-alphanumeric characters in the
    # row names (index), replace with underscore '_'
    # build a list with the new row names, assign the list to dataframe

    parsedindex = []
    for index in df.index:
        parsedindex.append(index.replace(' ', '_').replace('-', '_')
                                .replace('.', '_').replace('(', '_')
                                .replace(')', '_').replace('[', '_')
                                .replace(']', '_').replace(':', '_')
                                .replace('+', '_').replace('/', '_')
                                .replace('"', '_').replace(',', '_'))
    df.index = parsedindex


    return df

