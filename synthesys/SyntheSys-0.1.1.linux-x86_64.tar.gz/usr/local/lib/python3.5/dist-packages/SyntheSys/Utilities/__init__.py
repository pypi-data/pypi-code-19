
__all__=["BugManager", "GUITools", "RemoteOperations", "Timer", "ColoredLogging", "HtmlTextView", "Internet", "Simulation", "GenericGUI", "Misc", "Threads"]

import signal, logging, sys

CurrentProcess = None 
Executable     = None

#=================================================================================
def SigIntHandler(Sig, frame):
	"""
	SIGINT signal handler: kill subprocess
	"""
	global CurrentProcess, Executable
	if CurrentProcess is None: 
		logging.warning("Ctrl+C pressed: exit.")
	else:
		logging.warning("Ctrl+C pressed, killing subprocess '{0}'...".format(Executable))
		if CurrentProcess.poll() is None: 
			try: os.killpg(CurrentProcess.pid, signal.SIGTERM)
			except: pass
	sys.exit(0)

#------------------------------------------       
signal.signal(signal.SIGINT, SigIntHandler)
#------------------------------------------



