#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Jingyu Wang <badpasta@gmail.com>
# 
# Environment:
# Python by version 2.7.
# request = ['xlrd']

import sys
import xlrd
import time


def loadXlsx(file_name):

    workbook = xlrd.open_workbook(file_name)

    the_sheet = workbook.sheet_by_index(0) 
    cols_num = the_sheet.ncols
    rows_num = the_sheet.nrows

    sheet_context = filter(lambda g: g[0] is not '', 
                            [map(lambda x: the_sheet.cell(r_num, x).value, 
                                range(0, cols_num)) for r_num in range(0, rows_num)])

    data_tables = sheet_context[0]
    data_list = map(lambda row: dict(zip(data_tables, row)), sheet_context[1:])
    return data_list
