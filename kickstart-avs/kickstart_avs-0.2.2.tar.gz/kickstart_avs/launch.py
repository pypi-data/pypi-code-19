#!/usr/bin/env python
#==============================================================================

#title           :launch.py
#description     :This is class that will take care of lauching avs
#author		     :Ajay Krishna Teja Kavuri
#date            :08092017
#version         :0.4
#==============================================================================

# Libraries
import libtmux
from sultan.api import Sultan
import subprocess
import traceback
import time
#==============================================================================

class Launch():

    # Initialization
    def __init__(self):
        # define a default wake work engine
        self.wkeWrdEngine = "sensory"

        #define a dict of allowed strings as wake word engines
        self.wkeWrdEngineSet = set(['kitt_ai','sensory'])

        # Start a tmux session and grab the tmux server session, window
        self.tmuxSessionName = "kickstart_avs_session"
        self.tMuxWindowName = "kickstart_avs_window"
        self.startTmux()
        self.tMuxServer = libtmux.Server()
        self.tmuxSession = self.tMuxServer.find_where({ "session_name": self.tmuxSessionName })
        self.tMuxWndw = self.tmuxSession.attached_window

        # Debug statement
        # print "Hang tight!"

    # Method will get the current wake word engine
    def getWakeWordEngine(self):
        return self.wkeWrdEngine

    # Method will set the wake word engine
    def setWakeWordEngine(self,wkeWrdEngine="sensory"):
        # check weather it's allowed
        if wkeWrdEngine in self.wkeWrdEngineSet:
            self.wkeWrdEngine = wkeWrdEngine
        else:
            raise ValueError('Only kitt_ai or sensory are supported')

    # Check if tmux is installed
    def isTmuxInstalled(self):
        # Variable for output
        sultanOutput = ""

        # Check if the package is installed
        sultanOutput = Sultan().sudo('dpkg -s tmux | grep Status').run()
        # Return based on the output
        if sultanOutput == ['Status: install ok installed']:
            return True
        else:
            return False

    # start a tmux session
    def startTmux(self):
        # Commands for the execution
        tmuxNewSessCommand = "tmux new-session -n "+self.tMuxWindowName+" -s "+self.tmuxSessionName+" -d"
        tmuxInstallCommand = "apt-get install -y tmux"
        # Check if installed
        if not self.isTmuxInstalled():
            # Install tmux
            sultanOutput = Sultan().sudo(tmuxInstallCommand).run()
        # Start a new session
        self.runBash(tmuxNewSessCommand)
        return True

    # run a bash script
    def runBash(self,bashCommand=""):
        try:
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
        except:
            raise ValueError('Bash command not executable')

    # the method will create pane with the given name
    def createTmuxPane(self,paneName):
        try:
            paneName = self.tMuxWndw.split_window(attach=False)
            return paneName
        except:
            return False

    # this method will launch the avs commands:
    # 1. CS: companion service
    # 2. JC: Java Client
    # 3. WW: Wake Word Client
    def launchAVS(self):
        # define the commands to run
        cmdDir = "cd ~/Desktop/alexa-avs-sample-app/samples"
        cmdDict = {
                    'paneCS':'cd companionService && npm start',
                    'paneJC':'cd javaclient && mvn exec:exec',
                    'paneWW':'cd wakeWordAgent/src && ./wakeWordAgent -e '+self.getWakeWordEngine()
        }
        paneLst = ['paneCS','paneJC','paneWW']

        # Now, create a pane and execute the commands
        try:
            # loop and create
            for thisPane in paneLst:
                curCmd = cmdDict[thisPane]
                thisPane = self.createTmuxPane(thisPane)
                # check to see if created
                if thisPane:
                    thisPane.send_keys(cmdDir+" && "+curCmd)
                # wait and run for better queuing
                time.sleep(5)
        except:
            # print(traceback.format_exc())
            return False
