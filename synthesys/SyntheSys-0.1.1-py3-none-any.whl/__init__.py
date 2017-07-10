#!/usr/bin/python


__all__=["YANGO", "SysGen", "Analysis"]

import os, sys

#================NORMAL SYNTHESIS MODULES================
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm
from SyntheSys.Analysis.SyntheSys_Testbench import SyntheSys_Testbench
from SyntheSys.Synthesis.Synthesis import SyntheSys_Synthesize

Algorithm=SyntheSys_Algorithm
Testbench=SyntheSys_Testbench
Synthesize=SyntheSys_Synthesize

from SyntheSys.SysGen import SWLIBRARYPATH
sys.path.append(os.path.join(SWLIBRARYPATH, '..'))
import importlib
SoftLib = importlib.import_module('SW')
#==============OTHERS===========


	
