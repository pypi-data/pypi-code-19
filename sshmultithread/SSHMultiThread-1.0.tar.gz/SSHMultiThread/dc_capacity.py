import datetime
from Queue import Queue
from threading import Thread, current_thread
from threading import Lock
import ConfigParser
import subprocess
import types
import os
import csv
import json
CSVOPFILE="main.csv"
lock=Lock()
class label(Exception): pass
class ThreadPool:
	"""Pool of threads consuming tasks from a queue"""
	def __init__(self, num_threads=None):
		if num_threads == None:
			pass
		else:
			self.tasks = Queue(num_threads)
			for _ in range(num_threads): Worker(self.tasks)
	def add_task(self, host,customer):
		"""Add a task to the queue"""
		self.tasks.put((host,customer))
	def wait_completion(self):
		"""Wait for completion of all the tasks in the queue"""
		self.tasks.join()
	def replace(x):
		if x=='192.168.2.102':
			return host
		return x
class Worker(Thread,ThreadPool):
	"""Thread executing tasks"""
	def __init__(self, tasks=None):
		"""Creating a new instance"""
		if tasks == None:
			pass
		else:
			Thread.__init__(self)
			self.tasks = tasks
			self.daemon = True
			self.start()
			self.main_list=[]
	def run(self):
		"""This will be executed by threads"""
		while True:
			self.host,self.customer = self.tasks.get()
			try:
				self.cmd_exec()
			except Exception, e:
				print e
			finally
				self.tasks.task_done()
	def cmd_exec(self):
		with open('commands.ini','r') as com:
			cmd_flag=0
			for cmd in line:
				lst=(cmd.rstrip()).split('#')
				output = subprocess.Popen([self.host if x=='root@192.168.2.101' else x for x in lst],stdout=subprocess.PIPE).communicate()[0]
				if cmd_flag==0:# As every command will have different parsing style
				
				if cmd_flag==1:# As every command will have different parsing style
				#So on




		self.main_list.append('\n')
		self.string=''.join(map(str, self.main_list))
		logmain(self.string)# Writting file in one short by each thread
		self.main_list=[]
def section1():
	"""The html page will have various sections. This is for section 1"""

def section2():
        """The html page will have various sections. This is for section 2"""

if __name__ == '__main__':
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        Config = ConfigParser.ConfigParser()
        Config.read("inventory.ini")
        nocustcsv=open('nocust.csv','w')
        accdetails=open('accDetails.json','w')
        mhtml=open('mainhtml.html','w')
        nossh_file=open('nossh.txt', 'w')
        licsv=open('licExpire.csv','w')
        mainhtml(mhtml)
        accdetails.write('{')
        licsv.write('{')
        def logmain(msg):
                lock.acquire()
                f_html.write(msg)
                lock.release()
        def loglic(msg):
                lock.acquire()
                licsv.write(msg)
                licsv.write('\n')
                print (current_thread().name," :","Accquired lock")
                lock.release()
                print (current_thread().name," :","Released lock")
        def lognocus(msg):
                lock.acquire()
                nocustcsv.write(msg)
                lock.release()
        def logaacdetails(msg):
                lock.acquire()
                accdetails.write(msg)
                lock.release()
        def logexp(msg):
                lock.acquire()
                licsv.write(msg)
                lock.release()
	pool = ThreadPool(5)
        for each_section in Config.sections():
                customer=Config.get(each_section,'customer')
                host=Config.get(each_section,'host')
                pool.add_task(each_section,host,customer)
        pool.wait_completion()

	section1()
        section2()
	#All section methods goes here
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
