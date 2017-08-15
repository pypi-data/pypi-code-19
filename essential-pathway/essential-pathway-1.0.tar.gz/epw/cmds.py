#!/usr/bin/env python
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#cmd message class
#Essential Pathways v1.0
#Author:realasking
#Email:realasking@gmail.com,tomwangsim@163.com
#Aug-06,2017,in USTB
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import sys 
import os
import re
import shutil

class ops:
    def __init__(self):
        pass 

    def module_backup(self,df,bf):
        shutil.copy(df,bf)

    def module_restore(self,bf,df):
        shutil.copy(bf,df)

    def uninstall(self,module_name,module_file):
        os.system('module unload '+module_name)
        #print(module_name)
        #print(module_file)
        shutil.rmtree(module_file,ignore_errors=True)
        os.remove(module_file)
  
class warnings:
    def __init__(self):
        pass 

    def Inerror(self):
        print("Input command not supported.\n")
    
    def Merror(self):
        print('Please install tcl version Environment Modules, and then setup your custom modules\' path using $HOME/.modulespath file\n')

    def Mnerror(self):
        print('Please define a writable path to save your private modules\n')

    def Perror(self):
        print("Input folder path not exist.\n")

    def Pderror(self):
        print("The pathway is not defined yet.\n")

    def Outhelp(self):
        print("Essential PATHWAY v1.0\n")
        print("This script is released under the GPLv3 License\n")
        print("Author:Zheng Wang <realasking@qq.com,tomwangsim@163.com>\n")
        print("2017-08-06\n")
        print("Usage:\n")
        print("      *Quckly add current foler to a pathway:")
        print("       $ep a PATHWAY_NAME\n")
        print("      *Listing exsit pathways:")
        print("       $ep l\n")
        print("      *Create a pathway:")
        print("       $ep a PATHWAY_NAME PATH_TO_YOUR_FOLDER\n")
        print("      *Make or change a short comment for an exists pathway:")
        print("       $ep c PATHWAY_NAME\n")
        print("      *Modify a pathway:")
        print("       $ep m PATHWAY_NAME PATH_TO_NEW_FOLDER\n")
        print("      *Delete a pathway:")
        print("       $ep d PATHWAY_NAME\n")
        print("      *Check paths\' availabilities and automatic delete invalid ones:")
        print("       $ep k\n")
        print("      *Refresh the Env-module:")
        print("       $ep r\n")
        print("      *Backup settings:")
        print("       $ep b\n")
        print("      *Uninstall all settings:")
        print("       $ep u\n")

