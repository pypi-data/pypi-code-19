# -*- coding: utf-8 -*-
#****g* ganessa.th/About
# PURPOSE
#   The module ganessa.th provides a Python interface to Ganessa_TH.dll
#   kernel (equivalent to Picalor kernel). It is based on ganessa.sim
#   It will be extended as needed.
# INSTALLATION
#   numpy must be installed
#
# USE
#   Syntax:
#   * import ganessa.th as gt
#   * gt.cmdfile('my file.dat')
#
# CONTENT
#   See ganessa.sim
#
# REMARK
#   Any suggestion for extending / improving can be mailed to: piccolo@safege.fr
#****
'''
Created on 26 mai 2015

@author: Jarrige_Pi
'''
import os.path
execfile(os.path.join(os.path.dirname(__file__), 'sim.py'))

