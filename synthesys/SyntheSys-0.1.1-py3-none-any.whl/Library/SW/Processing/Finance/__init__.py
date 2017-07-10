#! /usr/bin/python3
"""
Finance module !
"""
import os, sys

__all__=["BOPMUnit", "BOPMUnit_Add",]


#----------------------------------------------
from SyntheSys.Library.SW.Processing.Finance.BOPMUnit import __BASICBLOCK__BOPMUnit
BOPM_Unit = __BASICBLOCK__BOPMUnit()
from SyntheSys.Library.SW.Processing.Finance.BOPMUnit_Add import __BASICBLOCK__BOPMUnit_Add
BOPM_Unit_Add = __BASICBLOCK__BOPMUnit_Add()








