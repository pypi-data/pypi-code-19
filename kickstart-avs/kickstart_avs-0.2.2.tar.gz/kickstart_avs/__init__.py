#!/usr/bin/env python
#==============================================================================

#title           :__init__.py
#description     :Initialization script to launch the project
#author		     :Ajay Krishna Teja Kavuri
#date            :08092017
#version         :0.2
#==============================================================================

# Libraries
from .launch import *
#==============================================================================

# This will steer the launch class to kickstart_avs
def kickstartAVS():

    # Get the instance of launch
    thisLaunch = Launch()

    # Trigger the launchAVS
    thisLaunch.launchAVS()
