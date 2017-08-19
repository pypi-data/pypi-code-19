import threading
from .implementation import Dictionary

class DictionaryThread(threading.Thread):
	def __init__(self,dictionary):
		threading.Thread.__init__(self)
		self.dict = dictionary
		self.daemon = True
		self.dictionaryobject = None

	def run(self):
		self.dictionaryobject = Dictionary(self.dict) # this process takes a while, running it in a thread makes life easier

	def isFinished(self):
		return self.dictionaryobject is not None

	def getObject(self):
		return self.dictionaryobject

def getDict(file):
	thread = DictionaryThread(file)
	thread.start()
	return thread

# Note: getDict is meant to be used as so:

# dict = dictionary.getDict("american_english_small")

# Then, when we need to use the dictionary:

# while not dict.isFinished(): # Block until dictionary is ready to use
#	time.sleep(15)
# for i in dict.getObject().startsWith('a'):
#	print(i[0])
