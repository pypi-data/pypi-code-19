#!/usr/bin/env python
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#einit
#Essential Pathways v1.0
#Author:realasking
#Email:realasking@gmail.com,tomwangsim@163.com
#Aug-06,2017,in USTB
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import sys
import os
import re
import sqlite3
import shutil
from epw import cmds

class einit():
      def __init__(self,cfolder,dbf,mname):
          self.home=os.path.expanduser("~")
          #cfolder should be .ep 
          self.conf_folder=cfolder 
          #dbf should be ep.db
          self.dbfile=dbf
          #mname should be epath
          self.module_name=mname
          self.folder=self.home+'/'+self.conf_folder
          self.df=self.folder+'/'+self.dbfile
          self.bf=self.home+'/BEP'
          self.info=cmds.warnings()

          if not os.path.exists(self.folder):
             os.makedirs(self.folder,exist_ok=True)

          if not os.path.exists(self.bf):
             os.makedirs(self.bf,exist_ok=True)

          if not os.path.isfile(self.home+'/.modulespath'):
             self.info.Merror()
             exit()
          else:
             setmf=0
          for modules_folder in re.split(':',os.environ['MODULEPATH']):
              if os.access(modules_folder, os.W_OK):
                  setmf=1
                  self.module_file=modules_folder+'/'+self.module_name
                  break
          if setmf==0:
             self.info.Mnerror()
             exit()

