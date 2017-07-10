
import logging, sys, os

#try: 
#	from fabric.api import task, run, roles, execute, env
#	from fabric.tasks import Task
#	from fabric.colors import blue, cyan, green, magenta, red, white, yellow	
#	from fabric.context_managers import cd, hide, lcd, path, prefix, settings, show
#	from fabric.contrib.console import confirm
#	from fabric.contrib import files	
#	from fabric.contrib.project import upload_project
#	#from fabric.decorators	
#	from fabric.network import disconnect_all
#	from fabric.operations import get, put, reboot, run, require, local, get, sudo, prompt, open_shell
#	from fabric.utils import abort, fastprint, indent, puts, warn
#	USE_FABRIC=True
#except:
#	USE_FABRIC=False
	

import os
#import hashlib
import datetime
import getpass
import shlex
import shutil
import tarfile
import tempfile
import time
import hashlib

from Utilities import Timer

import getpass
try: import configparser
except: import ConfigParser as configparser

#==================================================================
class RemoteOperations():
	#------------------------------------------------------------------------------
	def __init__(self, RemoteSubFolder="UnknownTool"):
		"""
		Environment variables settings
		"""
		self.RemoteHost = None
		self.UseOpenSSH = True
		#---------
#		LocalUser=getpass.getuser()
		#---------
#		self.LocalWorkingPath=os.path.normpath(os.path.join('~', '.adacsys', 'tmp', RemoteSubFolder, "{0}-{1}".format(LocalUser, Timer.TimeStamp())))
#		self.HostWorkingPath='~/FPGA_Synthesis/tmp/RemoteFiles/{0}/{1}'.format(RemoteSubFolder, "{0}-{1}".format(LocalUser, Timer.TimeStamp()))
	#------------------------------------------------------------------------------
#	def SetLocalWorkingPath(self, Path=None):
#		"""
#		Set working directories.
#		"""
#		if os.path.isdir(Path): 
#			self.LocalWorkingPath=Path
#			return self.LocalWorkingPath
#		else:
#			return None
	#------------------------------------------------------------------------------
	def SetRemoteHost(self, RemoteHost, PromptID=False, Config=None):
		"""
		Set Remote Mode to True/False.
		"""
		self.RemoteHost=RemoteHost
#		if self.RemoteHost:
			#---------
#			if Config is None:
#				USER, PASSWORD, HOST, PORT, KEYFILE, self.UseOpenSSH = GetConnectionParam()
#			elif os.path.isfile(Config):
#				#----------------------------------------------------
#				logging.info("Using a configuration file.")
#				for USER, PASSWORD, HOST, PORT in ConfigParse(Config, PromptID=PromptID):
#					if None in [USER, PASSWORD, HOST, PORT]: return False
#					else:
#						if not self.Configure(User=USER, Password=PASSWORD, Host=HOST, Port=PORT): 
#							logging.debug("Connexion failed => switch to next configuration.")
#							continue
#						else:
#							logging.debug("User config valid.")
#							return True
#				logging.debug("No more configuration to try.")
#				return False
#						
#			else:
#				USER, PASSWORD, HOST, PORT, KeyFile, UseOpenSSH = GetConnectionParam()
#				if Config.count(':'): 
#					HOST, PORT = Config.split(':')
#				else: 
#					HOST, PORT = Config, None
#				#-----------------------------------------------
#				if PromptID:
#					USER=raw_input("[{0}] Username: ".format(HOST))
#					PASSWORD=getpass.getpass("[{0}] Password: ".format(HOST))
#				#-----------------------------------------------
##				logging.debug("User={0}, Host={1}, Port={2}".format(USER, HOST, PORT))
#			#---------
##			logging.debug("Configuration fetched. Now try a connection.")
#			return self.Configure(User=USER, Password=PASSWORD, Host=HOST, Port=PORT, KeyFile=KEYFILE)
#		else:
#			return True
	#------------------------------------------------------------------------------
#	def Configure(self, User=None, Password=None, Host=None, Port=None, KeyFile=None, ConfigName=None):
#		"""
#		Configure connection parameters
#		"""
#		self.ConfigName=ConfigName
#		try: 
#			env.use_ssh_config = True
#			if KeyFile: env.key_filename = KeyFile
#			if Password: env.password=Password
#	#		env.use_ssh_config=False
#			env.reject_unknown_hosts=False
#			if not Port:
#				env.host_string="{0}@{1}".format(User, Host)
#			else:
#				env.host_string="{0}@{1}:{2}".format(User, Host, Port)
#		except: pass
##		logging.debug("Remote host_string: {0}".format(env.host_string))
#		self.Host=Host
#		self.Port=Port
#		if self.TestConnection():
#			logging.info("Server connection initialized.")
#			return True
#		else:
#			logging.error("Unable to connect to host '{0}' with specified identifiers.".format(self.Host))
#			return False
	#------------------------------------------------------------------------------
#	def TestConnection(self):
#		"""
#		Test if identifiers are ok. 
#		It's a silent test function.
#		"""
##		logging.debug("Connection test...")
##		original_stderr = sys.stderr  # keep a reference to STDOUT
##		sys.stderr = NullDevice()  # redirect the real STDOUT
#		try:
##			with Silence(sys.stderr):
#			self.RemoteRun(Command="uname -m", abort_on_prompts='True', warn_only=True)
#			self.HostArchi  = 64
#		except:
#			logging.error("Connection test: failed.")
#			return False
#		
##		logging.debug("Host architecture: '{0}'.".format(self.HostArchi))
##		logging.debug("Connection test: passed.")
#		return True
	#------------------------------------------------------------------------------
#	def HostArchitecture(self):
#		"""
#		return a string format for host architecture (32 or 64bit).
#		"""
#		with settings(hide('everything'), abort_on_prompts='True', warn_only=True):
#			Res=run("uname -m")
#			if Res.failed:
#				return "64" # By default return 64bit
#			else: 
#				Archi = Res[:]
#				if "64" in Archi:
#					return "64"
#				else: return "32"
	#------------------------------------------------------------------------------
#	def HostISEVersion(self):
#		"""
#		return a string format for host ISE higher version installed (32 or 64).
#		"""
#		with settings(hide('everything'), abort_on_prompts='True', warn_only=True):
#			Res=run("ls /opt/Xilinx")
#			if Res.failed:
#				return "13.1" # By default return 13.1
#			else:
#				VersionList = str(Res[:]).split()
#				return sorted(VersionList).pop(-1)
#		
#		return "13.1" # By default return 13.1
	#------------------------------------------------------------------------------
	def Disconnect(self):
		"""
		Configure connection parameters
		"""
		try: disconnect_all()
		except: pass
		return
	#------------------------------------------------------------------------------
	def SendPaths(self, DirList=[], FileDict={}):  
		"""
		Send a bunch of local path to remote host. Create, eventually, some host directories before.
			DirList  : list of directories to be created on host.
			FileDict : pair LocalPath:HostPath. Local paths to be sent to a Host path.
		"""
		logging.debug("Send data to remote host.")
#		BaseDirectory="~/.adacsys/tmp/a remote test/"
#		if not os.path.isdir(os.path.abspath(os.path.normpath(os.path.expanduser(BaseDirectory)))): 
#			logging.debug("Create directory '{0}'".format(os.path.abspath(os.path.normpath(os.path.expanduser(BaseDirectory)))))
#			os.makedirs(os.path.abspath(os.path.normpath(os.path.expanduser(BaseDirectory))))
		for Directory in DirList:
			try: 
				logging.debug("Create directory '{0}'.".format(Directory))
				if self.RemoteRun(Command="mkdir -p {0}".format(Directory), ScriptsToSource=[], abort_on_prompts='True', warn_only=True) is False:
					logging.error("Remote host configuration: unable to create directory '{0}'.".format(Directory))
					return False
			except: 
				logging.error("Remote host configuration: unable to create directory '{0}'.".format(Directory))
				return False
	
		TempPath=tempfile.mkdtemp(suffix='', prefix='tmp', dir=None)
		#os.path.abspath(os.path.normpath(os.path.expanduser("~/.adacsys/tmp/a_remote/")))
		Archive=os.path.join(TempPath, "Bundle.tar.gz")
		logging.debug("Create archive '{0}'".format(Archive))
#		logging.debug("Local '{0}' archive created".format(Archive))

		#-=-=-=-=-=-=-=-=-=-=-=-
		with tarfile.open(Archive, "w:gz") as TGZFile:
			for LocalPath, HostPath in FileDict.items():
				logging.debug("Move '{0}' to '{1}'.".format(LocalPath, HostPath))
				#-----------------------------------------------------
				if os.path.exists(LocalPath):
					LPath=os.path.abspath(os.path.normpath(os.path.expanduser(LocalPath)))
					logging.debug("Add '{0}' to the archive.".format(LPath))
					TGZFile.add(LPath, arcname=os.path.basename(LPath), recursive=True, exclude=None, filter=None)
				else: logging.error("No such directory '{0}'".format(LocalPath)); return False
		#-=-=-=-=-=-=-=-=-=-=-=-

		if not os.path.isfile(Archive):
			logging.error("Unable to create tar.gz archive '{0}'.".format(Archive))
			return False
		
		if self.UploadToHost(LocalPath=Archive, HostPath=HostPath) is False:
			logging.error("Upload failure")
			return False
		os.remove(Archive)
			
		RemoteArchive=os.path.join(HostPath, os.path.basename(Archive))
		if self.RemoteRun(Command="tar -xzvf {1} --directory={0}".format(HostPath, RemoteArchive), ScriptsToSource=[], abort_on_prompts='True', warn_only=True) is False:
			logging.error("Compression failure.")
			return False
		logging.info("Remote .tar.gz file successfully unpacked")

		#-=-=-=-=-=-=-=-=-=-=-=-
		logging.debug("Checksum operation.")
		LocalCheckSum = CheckSum(FilePath=LocalPath, Algo="md5")
		logging.debug("[LOCAL CHECKSUM] '{0}'  {1}".format(LocalCheckSum, LocalPath))
		
#					with settings(abort_on_prompts='True', warn_only=True):
		ChecksumCmd="md5sum {0}".format(RemoteArchive)
		Success=self.RemoteRun(Command=ChecksumCmd, ScriptsToSource=[], abort_on_prompts='True', warn_only=True)
		if self.RemoteRun(Command="rm {0}".format(RemoteArchive), ScriptsToSource=[], abort_on_prompts='True', warn_only=True) is False:
			logging.error("Archive removal failure.")
			return False
		if Success is True:
			RemoteCheckSum=ChecksumCmd
			if RemoteCheckSum!=ChecksumCmd:
				logging.error("File '{0}' checksum failed.".format(LocalPath))
				return False
		else:
			logging.error("Checksum command failed: {0}.".format(ChecksumCmd))
			logging.error("Host file '{0}' checksum failed.".format(HostFilePath))
			return False
			
		return True
	#------------------------------------------------------------------------------
	def CreateHostDir(self, DirList=[]):  
		"""
		DirList  : list of directories to be created on host.
		"""
		for Directory in DirList:
			try: 
				Command="mkdir -p {0}".format(Directory)
				logging.debug("Create directory '{0}'.".format(Directory))
				if self.RemoteRun(Command=Command, ScriptsToSource=[], abort_on_prompts='True', warn_only=True) is False:
					logging.error("Remote host configuration: unable to create directory '{0}'.".format(Directory))
					return False
			except: 
				logging.error("Remote host configuration: unable to create directory '{0}'.".format(Directory))
				return False
		return True
	#------------------------------------------------------------------------------
	def SendPathsRelative(self, FileDict, HostAbsPath):  
		"""
		Send a bunch of local path to remote host. Create, eventually, some host directories before.
			DirList  : list of directories to be created on host.
			FileDict : pair LocalPath:HostRelPath. Local paths to be sent to a Host path.
		"""
		logging.debug("Send data with relative path to remote host.")
	
		TempPath=tempfile.mkdtemp(suffix='', prefix='tmp', dir=None)
		#os.path.abspath(os.path.normpath(os.path.expanduser("~/.adacsys/tmp/a_remote/")))
		Archive=os.path.join(TempPath, "Bundle.tar.gz")
		logging.debug("Create archive '{0}'".format(Archive))
#		logging.debug("Local '{0}' archive created".format(Archive))

		#-=-=-=-=-=-=-=-=-=-=-=-
		with tarfile.open(Archive, "w:gz") as TGZFile:
			for LocalPath, HostRelPath in FileDict.items():
				logging.debug("Move '{0}' to '{1}' (relative:'{2}').".format(LocalPath, HostAbsPath, HostRelPath))
				#-----------------------------------------------------
				if os.path.exists(LocalPath):
					logging.debug("Add '{0}' to the archive.".format(os.path.basename(LocalPath)))
					TGZFile.add(LocalPath, arcname=HostRelPath, recursive=True, exclude=None, filter=None)
				else: logging.error("No such directory '{0}'".format(LocalPath)); return False
		#-=-=-=-=-=-=-=-=-=-=-=-

		if not os.path.isfile(Archive):
			logging.error("Unable to create tar.gz archive '{0}'.".format(Archive))
			return False
		
		if self.UploadToHost(LocalPath=Archive, HostPath=HostAbsPath) is False:
			logging.error("Upload failure")
			return False
		os.remove(Archive)
			
		RemoteArchive=os.path.join(HostAbsPath, os.path.basename(Archive))
		if self.RemoteRun(Command="tar -xzvf {1} --directory={0}".format(HostAbsPath, RemoteArchive), ScriptsToSource=[], abort_on_prompts='True', warn_only=True) is False:
			logging.error("Compression failure.")
			return False
		logging.info("Remote .tar.gz file successfully unpacked")

		#-=-=-=-=-=-=-=-=-=-=-=-
		logging.debug("Checksum operation.")
		LocalCheckSum = CheckSum(FilePath=LocalPath, Algo="md5")
		logging.debug("[LOCAL CHECKSUM] '{0}'  {1}".format(LocalCheckSum, LocalPath))
		
#					with settings(abort_on_prompts='True', warn_only=True):
		ChecksumCmd="md5sum {0}".format(RemoteArchive)
		Success=self.RemoteRun(Command=ChecksumCmd, ScriptsToSource=[], abort_on_prompts='True', warn_only=True)
		if self.RemoteRun(Command="rm {0}".format(RemoteArchive), ScriptsToSource=[], abort_on_prompts='True', warn_only=True) is False:
			logging.error("Archive removal failure.")
			return False
		if Success is True:
			RemoteCheckSum=ChecksumCmd
#			RemoteCheckSum=Res[:].split()[0]
#						logging.debug("[LOCAL] '{0}' checksum: {1}".format(LocalPath, LocalCheckSum))
#						logging.debug("[REMOTE]'{0}' checksum: {1}".format(HostFilePath, RemoteCheckSum))
			if RemoteCheckSum!=ChecksumCmd:
				logging.error("File '{0}' checksum failed.".format(LocalPath))
				return False
		else:
			logging.error("Checksum command failed: {0}.".format(ChecksumCmd))
#			logging.error("{0}.".format(Res[:]))
			logging.error("Host file '{0}' checksum failed.".format(HostFilePath))
			return False
		#-=-=-=-=-=-=-=-=-=-=-=-
#			else:
#				logging.error("[Remote host configuration] Sending data: unable to move '{0}' into '{1}' (missing?).".format(LocalPath, HostAbsPath))
#				return False
			
		return True
	#------------------------------------------------------------------------------
	def UploadToHost(self, LocalPath, HostPath, **Settings):
		"""
		Upload a local path to host.
		"""
		time.sleep(0.1)
		if self.UseOpenSSH is True:
			Res=self.SSH_COPY_TO(SourcePath=LocalPath, TargetPath=HostPath)
			if Res==0: return True
			else: return False
		else:
			with settings(**Settings):
				UploadedFiles=put(LocalPath, HostPath)
				if len(UploadedFiles)==0: return False
				else: return True
			
	#------------------------------------------------------------------------------
	def DownloadFromHost(self, HostPath, LocalPath, **Settings):
		"""
		Download a host path to local.
		"""	
		time.sleep(0.1)
		if self.UseOpenSSH is True:
			Res=self.SSH_COPY_FROM(SourcePath=HostPath, TargetPath=LocalPath)
			if Res==0: return True
			else: return False
		else:
			logging.warning("fabric not supported.")
#			with settings(**Settings):
#				UploadedFiles=get(HostPath, local_path=LocalPath)
#				if len(UploadedFiles)==0: return False
#				else: return True
	#------------------------------------------------------------------------------
	def RemoteRun(self, Command, ScriptsToSource=[], FromDirectory=None, XForwarding=False, **Settings):
		"""
		Run a command line on host bash console.
		"""
		time.sleep(0.1)
#		logging.debug("REMOTE RUN: '{0}'".format(Command))
		if self.UseOpenSSH is True:
			Res=self.SSH_RUN(Command=Command, ScriptsToSource=ScriptsToSource, FromDirectory=FromDirectory, XForwarding=XForwarding)
			if Res==0: return True
			else: return False
		else:
			logging.warning("fabric not supported.")
#			if len(ScriptsToSource):
#				SourceScript=ScriptsToSource.pop()
#				with prefix('source {0}'.format(SourceScript)):
#					return self.RemoteRun(Command, ScriptsToSource=ScriptsToSource, **Settings)
#			else:
#				with settings(**Settings):
#					Res=run(Command)
#					if Res.failed: return False
#					else: return True
	#------------------------------------------------------------------------------
	def SSH_RUN(self, Command, ScriptsToSource=[], FromDirectory=None, XForwarding=False):
		"""
		Run a command line on host with openssh.
		"""
		XOption="-Y" if XForwarding is True else ""
		if FromDirectory is None:
			SSH_CMD='ssh {2} -t {0} bash -lic \\"{1}\\"'.format(self.RemoteHost, Command, XOption)
		else:
			SSH_CMD='ssh {3} -t {0} "cd {2};bash -lic \\"{1}\\""'.format(self.RemoteHost, Command, FromDirectory, XOption)
		logging.debug("SSH command: '{0}'".format(SSH_CMD))
		
		RetVal=os.system(SSH_CMD)
#		os.system('ssh -t {0} "killall -s SIGKILL sshd"')
		return RetVal
	#------------------------------------------------------------------------------
	def SSH_COPY_TO(self, SourcePath, TargetPath):
		"""
		Run a command line on host with openssh.
		"""
		SSH_CMD="scp {SOURCE} {HOST}:{TARGET}".format(SOURCE=SourcePath, TARGET=TargetPath, HOST=self.RemoteHost)
		logging.debug("SSH command: '{0}'".format(SSH_CMD))
		return os.system(SSH_CMD)
	#------------------------------------------------------------------------------
	def SSH_COPY_FROM(self, SourcePath, TargetPath):
		"""
		Run a command line on host with openssh.
		"""
		SSH_CMD="scp {HOST}:{SOURCE} {TARGET}".format(SOURCE=SourcePath, TARGET=TargetPath, HOST=self.RemoteHost)
		logging.debug("SSH command: '{0}'".format(SSH_CMD))
		return os.system(SSH_CMD)
	#------------------------------------------------------------------------------
	def Hostcd(self, *argc, **argv):  
		"""
		Change current directory (context manager).
		"""	
		return cd(*argc, **argv)
	
#====================================================================
#def ConfigParse(Config, PromptID=False):
#	"""
#	Parse config ini file and return host, user, port and password found.
#		in the order "USER, PASSWORD, HOST, PORT"
#	"""
#	try:
#		Conf = configparser.RawConfigParser()
#		Conf.read(Config)
#	except configparser.ParsingError:
#		logging.error("Cannot parse configuration file '{0}'.".format(Config))
#		yield None, None, None, None
#	except IOError:
#		logging.error("Problem opening configuration file '{0}'.".format(Config))
#		yield None, None, None, None
#	except:
#		logging.error("Problem when attempting to read configuration file '{0}'.".format(Config))
#		yield None, None, None, None
#	
#	Sections=Conf.sections()
#	if len(Sections)==0:
#		logging.error("Nothing in configuration file: abort.")
#		yield None, None, None, None
#		
#	USER, PASSWORD, HOST, PORT, KeyFile, UseOpenSSH = GetConnectionParam()
#	for CONFIG in Sections:
#		logging.info("Trying configuration '{0}'.".format(CONFIG))
#		if Conf.has_option(CONFIG, "hostname"):
#			HOST = Conf.get(CONFIG, 'hostname')
#		else:
#			HOST = None
#		if Conf.has_option(CONFIG, "port"):
#			PORT = Conf.get(CONFIG, 'port')
#		else:
#			PORT = None
#	
#		if PromptID:
#			#-----------------------------
#			USER=raw_input("[{0}] Username: ".format(CONFIG))
#			PASSWORD=getpass.getpass("[{0}] Password: ".format(CONFIG))
#			#-----------------------------
#		yield USER, PASSWORD, HOST, PORT

#	yield None, None, None, None

#==================================================================
#def GetConnectionParam(): 
#	"""
#	return parameters for connection.
#	"""
#	User, Pass, Host, Port = "payetm", None, "CIME_TIMA", None# "ava-server", Pass = "5M96uL3t"
#	KeyFile = os.path.normpath(os.path.expanduser('~/.ssh/id_rsa.pub'))
#	logging.debug("User={0}, Host={1}, Port={2}, KeyFile={3}".format(User, Host, Port, KeyFile))
#	
##	if USE_FABRIC is True:
##		UseOpenSSH=True 
##	else:
##		UseOpenSSH=True 
#	return User, Pass, Host, Port, KeyFile, UseOpenSSH
	
				
#======================================================================
def CheckSum(FilePath, Algo="md5"):
	"""
	return check sum for specified "FilePath" calculated with algo "Algo".
	"""
	BLOCKSIZE=65536
	if Algo=="md5":    Hasher=hashlib.md5()
	elif Algo=="sha1": Hasher=hashlib.sha1()
	else:
		logging.error("[CheckSum] No such algorithm '{0}' defined for checksum.".format(Algo))
		return None
	
	with open(FilePath, 'rb') as FileChecked:
		Buf=FileChecked.read(BLOCKSIZE)
		while len(Buf)>0:
			Hasher.update(Buf)
			Buf=FileChecked.read(BLOCKSIZE)
	return Hasher.hexdigest()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
