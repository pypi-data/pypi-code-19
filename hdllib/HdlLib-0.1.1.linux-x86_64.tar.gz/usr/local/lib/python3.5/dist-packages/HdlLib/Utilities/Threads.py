
import threading, logging

 #============================================================================================================
def LaunchAsThread(Name = "Thread_Unknown", function = None, arglist = []):
	"Launch the function in a thread and return the thread identificator"
	
	thread = threading.Thread(None, function, Name, args=arglist, kwargs={})
	thread.start()
	logging.debug("Thread '{0}' Launched !!!".format(Name))	
	return thread

 #============================================================================================================
def Wait(Thread):
	if Thread:
		Thread.join()
		logging.debug("*** Thread <{0}> joined ***".format(Thread.name))
	else:
		pass
		#print "# Error: thread not running, failed to join."

 #============================================================================================================
class ThreadFunction(threading.Thread):        

	def __init__(self, Function, *args, **kwargs):
		self.args     = args
		self.kwargs   = kwargs
		self.Function = Function
		self.Returned = None
		threading.Thread.__init__(self)
		

	def run(self):
		self.Returned = self.Function(*self.args, **self.kwargs)
		
		
		
		
		
		
		
		
		
		
		
		
