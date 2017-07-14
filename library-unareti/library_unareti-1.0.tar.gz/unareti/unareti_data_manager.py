# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 09:46:44 2017

@author: dberetta
"""

def unareti_data_manager(FILE_LIST, CLEAN = True):
    
    # unareti_data_manager TAKES AS ARGUMENT
    #       - FILE_LIST:    a list of file in directories
    #       - CLEAN:        otional BOOLEAN, defaul = True
    
    # unareti_data_manager RETURNS
    #       - NONE
    
    # unareti_data_manager DOs
    #       - iterate over all the file in the FILE_LIST
    #       - check for input files type. If file is .rpt, passes the specific 
    #         file and the boolean CLEAN to rpt2csv_unareti. If 
    #         file is not .rpt, the function skips it.
    
    
    for idx_file in range (0, len(FILE_LIST)):

        if FILE_LIST[idx_file][-4:] == ".rpt":
            rpt2csv_unareti(FILE_LIST[idx_file], CLEAN)
        
