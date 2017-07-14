# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:58:38 2017

@author: dberetta
"""

def rpt2csv_unareti(INPUT_FILE, CLEAN = True):
    
    # rpt2csv_unareti TAKES AS ARGUMENT
    #       - INPUT_FILE:   .rpt WITH ID_Cabin, TimeStamp, Power Load
    #       - CLEAN:        otional BOOLEAN, defaul = True
    
    # rpt2csv_unareti RETURNS
    #       - NONE
    
    # rpt2csv_unareti DOs
    #       - check for file format error.
    #       - clean files from header and foot.
    #       - IF CLEAN = True (defualt) clean file from lines with Power Load = 0.
    #       - identifies different ID_Cabin within the file.
    #       - generate a .csv file for each ID_Cabin name. If a file with the same
    #         ID_Cabin is already present in the directory,then the new file is appendend.
      
    
    # IMPORT csv PYTHON LIBRARY -----------------------------------------------
    import csv
    import re


    # CHECK FOR FILE FORMAT
    if INPUT_FILE[-4:] != ".rpt":
        print("File %s IS NOT .rpt" % INPUT_FILE)
        return
    
    
    # READ INPUT FILE, CREATE A LIST OF LINES (TYPE STRING) -------------------
    input_file = open(INPUT_FILE, "r")
    input_lines = input_file.readlines()

    
    # REMOVE FILE HEADER (FIRST 3 LINES) AND FOOT (LAST 3 LINES)
    input_lines = input_lines[3:(len(input_lines)-3)]
   
    
    # SPLIT LINES INTO COLUMNS "IDCABIN", "TIMESTAMP", "POWER LOAD" -----------
    output_lines = []
    idx = 0
    while idx < len(input_lines):
        # splitting when occurs a number of whitespaces bigger than 2
        output_lines.append(re.split("  +", input_lines[idx]))
        # remove \n character in the last element of each list of list
        output_lines[idx][-1] = output_lines[idx][-1][:-1]
        idx += 1
    
    
    # OPTIONAL: DELETE ENTRIES WITH POWER LOAD EQUAL TO ZERO ------------------
    if CLEAN == True:
        idx = 0
        while idx < len(output_lines):
            if float(output_lines[idx][-1]) == 0:
                del output_lines[idx]
            else:
                idx += 1

    
    # GET IDCabin(s) IN FILE --------------------------------------------------
    ID_cabin = []
    for idx in range(0, len(output_lines)):
        # initialize file_name[] with the first IDCabin of the list of files
        if idx == 0:
            ID_cabin.append(output_lines[idx][0])
            # add IDCabin if not already present in file_name[]
        elif (idx != 0 and output_lines[idx][0] not in ID_cabin):
            ID_cabin.append(output_lines[idx][0])
    
    
    # WRITE TO FILES ENTRIES GROUPED BY IDCabin -------------------------------  
    for idx_cabin in range(0, len(ID_cabin)):
 
        OUTPUT_FILE = "%s/%s.csv" % (INPUT_FILE.rsplit("/",1)[0], ID_cabin[idx_cabin])
        file_out = open(OUTPUT_FILE, "a")
        # set csv.write options
        writer = csv.writer(file_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')    
        # write to file lines corresponding to the given ID_cabin
        for idx_line in range(0, len(output_lines)):
            if output_lines[idx_line][0] == ID_cabin[idx_cabin]:
                writer.writerow(output_lines[idx_line])
        file_out.close()