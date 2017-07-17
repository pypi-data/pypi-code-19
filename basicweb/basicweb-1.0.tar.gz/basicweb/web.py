from memory_profiler import profile
from SocketServer import ThreadingMixIn
import matplotlib
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import sqlite3 as sql
import Cookie
import random
import string
PORT_NUMBER = 8080
sessionDict={}
chars = string.ascii_letters + string.digits
def generateRandom(length):
	"""Return a random string of specified length (used for session id's)"""
	return ''.join([random.choice(chars) for i in range(length)])
#This class will handles any incoming request from
#the browser 
class SessionElement(object):
	"""Arbitrary objects, referenced by the session id"""
	pass
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
#HTTPServer is a simple subclass of SocketServer.TCPServer, and does not use multiple threads or processes to handle requests. To add threading or forking, create a new class using the appropriate mix-in from SocketServer.
class myHandler(BaseHTTPRequestHandler):
	cookie=Cookie.SimpleCookie()
	
	@profile	
	def do_GET(self):
		if self.path=="/":
			self.path="/index.html"
		try:
			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True
			if sendReply == True:
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
	@profile
	def do_POST(self):
		if self.path=="/send":
			self.path="/table.html"
			f = open(curdir + sep + self.path)
			#form = cgi.FieldStorage()
			print(self.rfile)
			form = cgi.FieldStorage(
				fp=self.rfile,#Faux file object attached to a socket object. 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			self.dbverify(form)
			#name = form.getvalue('name')
			#pass  = form.getvalue('pass')
			#print ("Yopur name is :" + form["name"].value)
			#self.cookie=Cookie.SimpleCookie()
			#selfranum=random.randint(100,1000000000)
			#self.cookie['Name']=form.getlist('name')[0]
			#self.cookie['Name']['expires']=1*60
			self.sessions()
			self.send_response(200)
			self.send_header('Cookie',self.cookie)
			self.end_headers()
			#self.wfile.write(form.keys())
			print (type(form))
			print(form.keys())
			print (form.list)
			print (form.getlist('name'))
			#self.wfile.write("<html><head><title>Title goes here.</title></head>")
			#self.wfile.write("<p>You accessed path: %s</p>" % self.path)
			#self.wfile.write("</body></html>")
			#self.wfile.write("""<form action="/logout" method="post"> First Name:""")
			#self.wfile.write(form.getlist('name')[0])
			#self.wfile.write("""<br /> Last Name: """)
			#self.wfile.write(form.getlist('pass')[0])
			#self.wfile.write("""<input type="submit" value="Submit" /></form>""")
			#self.wfile.write("</body></html>")
			self.wfile.write(f.read())
                        f.close()
		if self.path=="/logout":
			print ("In logout now:::: ")
			#self.cookie['Name']=""
			#self.cookie['Name']['expires']=""
			self.cookie["sessionId"]=""
			self.cookie['sessionId']['expires']=""
			del self.cookie["sessionId"]
			self.send_response(302)
			self.send_header("Location","/")
			self.end_headers()
		return
	@profile
	def sessions(self):
		if self.cookie.has_key("sessionId"):
			sessionId=self.cookie["sessionId"].value
		else:
			sessionId=generateRandom(8)
			self.cookie["sessionId"]=sessionId
			self.cookie['sessionId']['expires']=1*60
		try:
			sessionObject = sessionDict[sessionId]
		except KeyError:
			sessionObject = SessionElement()
			sessionDict[sessionId] = sessionObject
		return sessionObject
	@profile
	def dbverify(self,form):
		con = sql.connect("UserDB.db")
		cur = con.cursor()
		username_form=(form.getlist('name')[0])
		password_form=(form.getlist('pass')[0])
		print (username_form)
		print (password_form)	
		cur.execute("SELECT COUNT(1) FROM users WHERE username = (?);", [username_form])
		
		if cur.fetchone()[0]:
        		cur.execute("SELECT password FROM users WHERE username = (?);", [username_form])# FETCH THE HASHED PASSWORD
        		for row in cur.fetchall():
				print ("Row of 0 is :", row[0], " and password form is :", password_form)
                		if password_form  == row[0]:
                    			print ("Success")
                		else:
                    			print ("Invalid Credential")
					self.send_response(302)
                        		self.send_header("Location","/")
		else:
        		print ("Invalid Credential")
			self.send_response(302)
                        self.send_header("Location","/")
try:
	#Create a web server and define the handler to manage the
	#incoming request
	#server = HTTPServer(('', PORT_NUMBER), myHandler)
	server= ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
	print ('Started httpserver on port ' , PORT_NUMBER)
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print ('^C received, shutting down the web server')
	server.socket.close()

