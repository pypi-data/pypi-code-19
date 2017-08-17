import socket
import pickle
import json
import os
import threading


class DataStreamServer:
	s = None
	port = None
	host = None
	kill_server = False

	# variables
	users = []
	online_users = [] #contains list of - tuple(stream,username)
	online_users_username = []
	offline_dump = []

	def __init__(self):
		import json

	def initialize(self):
		with open(os.getcwd()+"/registered_users.pickle","w") as f:
			pickle.dump([],f)
		with open(os.getcwd()+"/offline_user_data.pickle","w") as f:
			pickle.dump([],f)
		return 200

	def register_user(self,username,password,name):
		d = dict()
		d['username'] = username
		d['password'] = password
		d['name'] = name
		d['presence'] = 0
		try:
			with open(os.getcwd()+"/registered_users.pickle","r") as f:
				self.users = pickle.load(f)
		except IOError:
			self.users = []
		try:
			for user in self.users:
				if user['username'] == username:
					raise ValueError("UserName Exists .")
			self.users.append(d)
		except ValueError as v:
			return 500
		with open(os.getcwd()+"/registered_users.pickle","w") as f:
			pickle.dump(self.users,f)

		try:
			with open(os.getcwd()+"/offline_user_data.pickle","r") as f:
				self.offline_dump = pickle.load(f)
		except IOError:
			self.offline_dump = []

		self.offline_dump.append({"username": []})
		with open(os.getcwd() + "/offline_user_data.pickle", "w") as f:
			pickle.dump(self.offline_dump,f)
		return d

	def receive(self,stream):
		thread_counter = 0
		while True:
			try:
				r = str(stream.recv(1024))
				dump = json.loads(r)
				if dump['type'] == "presence":
					with open(os.getcwd()+"/registered_users.pickle","r") as f:
						self.users = pickle.load(f)
						for user in self.users:
							if user['username'] == dump['username']:
								user['presence'] = dump['is_online']
					#for saving stream class - socket class
					if thread_counter == 0:
						u = (stream ,dump['username'])
						self.online_users.append(u)
						self.online_users_username.append(str(dump['username']))
						thread_counter = thread_counter+1

				elif dump['type'] == "registration":
					self.register_user(username=dump['username'],password=dump['password'],name=dump['name'])

				elif dump['type'] == "message":
					if str(dump['to_user']) in self.online_users_username:#if 'to' is online
						for to_user_stream,username in self.online_users:
							if username == dump['to_user']:
								to_user_stream.send(json.dumps(dump))
								break
					else:
						with open(os.getcwd()+"/offline_user_data.pickle","r") as f:
							self.offline_dump = pickle.load(f)
						self.offline_dump[dump['to_user']].append(dump)
						with open(os.getcwd()+"/offline_user_data.pickle","w") as f:
							pickle.dump(self.offline_dump,f)
				
			except Exception as e:#can be raised to kill client listening thread
				break
		return True

	# def send(self,stream):
	# 	while True:
	# 		m = str(raw_input())
	# 		if m == "purge":
	# 			print "inside purge"
	# 			c.sendall("Server left the conversation..")
	# 			s.close()
	# 			print "Connection closed at your end."
	# 			break
	# 		stream.sendall(m+'\n')
	# 	return True

	class serverThread(threading.Thread):
		thread_stream = None
		parent_context = None

		def __init__(self,stream,context):
			threading.Thread.__init__(self)
			self.thread_stream = stream
			self.parent_context = context

		def run(self):
			self.parent_context.receive(self.thread_stream)

	def start_server(self,p=12301):
		self.s = socket.socket()  # Create a socket object
		self.host = socket.gethostname()  # Get local machine name
		self.port = p  # Reserve a port for your service.

		self.s.bind(('0.0.0.0', self.port))  # Bind to the port
		self.s.listen(5)

		try:
			while self.kill_server is not True:
				d = dict()
				c, addr = self.s.accept()  # Establish connection with client.
				t1 = self.serverThread(stream=c,context=self)
				t1.daemon = True
				t1.start()
		except Exception as e:
			print "Error:" + str(e)

	def stop_server(self):
		self.kill_server = False
		self.s.close()
		return 200

	# class destructor
	def __del__(self):
		stop_server()
		del s