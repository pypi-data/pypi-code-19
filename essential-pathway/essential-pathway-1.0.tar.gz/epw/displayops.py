#!/usr/bin/env python
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#A class for display properties
#Essential Pathways v1.0
#Author:realasking
#Email:realasking@gmail.com,tomwangsim@163.com
#Aug-06,2017,in USTB
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import sys
import os
import re
import shutil

class screenformat:
      max_tty_rows=0
      max_tty_line_width=0
      fullptlength=0
      namelengthmax=0
      waylengthmax=0

      def __init__(self):
          arows,awidth=os.popen('stty size', 'r').read().split() 
          self.max_tty_rows=int(arows)
          self.max_tty_line_width=int(awidth)
    
      #obtain tty width, and set columns' widths automatically
      def size_calc(self,fileds):
          self.fullptlength=self.max_tty_line_width-3*int(fileds)-1
          self.namelengthmax=int(0.3*self.fullptlength)
          self.waylengthmax=int((self.fullptlength-self.namelengthmax)/(int(fileds)-1.0))

      #formatting strings to fit table length
      def string_formatting(self,data,filed_max_width):
          all_length=0
          fdata=""
          for cha in data:
               if all_length+2<filed_max_width:
                   fdata=fdata+cha 
                   all_length=all_length+1
               else:
                   all_length=1
                   fdata=fdata+"\n"+cha 
          return fdata

