import riffa
import array
import sys, os, struct, logging
import argparse

logging.basicConfig(filename=None, format='%(levelname)s: %(message)s', level=logging.INFO)

#=============================================================
#def PrintUsage():
#	print("Usage:")
#	print("\tpython3 TestRiffa.py OptionNb")
#	print("\twith options:")
#	print("\t\t* List          - List available FPGA")
#	print("\t\t* Reset  ID     - Reset FPGA ID")
#	print("\t\t* Send   File   - Send content of binary file")
#	print("\t\t* Config [File] - download a design to FPGA (default: reference design)")
#	print("\t\t* Loopback      - Send/receive 200 32bit words")
	
#=============================================================
# Rescan PCIe devices
def ScanFpga():
	logging.debug("Rescan PCIe devices...")
	os.system('sudo sh -c "echo 1 > /sys/bus/pci/rescan"')
	logging.debug("done.")
	
#=============================================================
# Reload PCIe riffa driver
def ReloadRiffaDriver():
	logging.debug("Reload Riffa driver...")
	os.system("sudo rmmod riffa")
	PcieFolder="/sys/bus/pci/devices/0000:01:00.0/"
	if os.path.isdir(PcieFolder):
		os.system('sudo sh -c "echo 1 > /sys/bus/pci/devices/0000:01:00.0/remove"')
#	else:
#		logging.error("No such folder '{0}'. Is the device connected ?".format(PcieFolder))
	os.system("sudo modprobe riffa")
	logging.debug("done.")
	
#=============================================================
# List riffa PCIe devices
def ListFpga(ReloadDriver=False):
	#-------------------------------
	if ReloadDriver is True:
		ReloadRiffaDriver()
		ScanFpga()
		DevicesInfo=riffa.fpga_list()
		if DevicesInfo is None:
			Found=False
		else:
			Found=True
	else:
		DevicesInfo=riffa.fpga_list()
		if DevicesInfo is None:
			if input("No FPGA found. Do you want to reload riffa driver ? (Y/N)").lower()=='y':
				ReloadRiffaDriver()
				ScanFpga()
				DevicesInfo=riffa.fpga_list()
				if DevicesInfo is None:
					Found=False
				else:
					Found=True
			Found=False
		else:
			Found=True
	#-------------------------------
	if Found is False:
		logging.error("No Riffa FPGA found. Aborted.")
		logging.debug("ls -la /sys/bus/pci/devices/")
		os.system("ls /sys/bus/pci/devices/")
		sys.exit(1)
	else:
		logging.info("Number of devices: {0}".format(DevicesInfo.num_fpgas))
		for i in range(DevicesInfo.num_fpgas):
			logging.info("\t {0}: id:{1}".format(i, DevicesInfo.id[i]))
			logging.info("\t {0}: num_chnls:{1}".format(i, DevicesInfo.num_chnls[i]))
			logging.info("\t {0}: name:{1}".format(i, DevicesInfo.name[i].value))
			logging.info("\t {0}: vendor id:{1:04X}".format(i, DevicesInfo.vendor_id[i]))
			logging.info("\t {0}: device id:{1:04X}".format(i, DevicesInfo.device_id[i]))
	
#=============================================================
# List riffa PCIe devices
def ResetFpga(ID):
	# Get the device with id
	logging.debug("Open FPGA", ID)
	Fpga = riffa.fpga_open(ID)
	if Fpga is None:
		logging.error("Could not get FPGA", ID)
		sys.exit(1)

	# Reset
	logging.debug("Reset FPGA {0}....".format(ID))
	riffa.fpga_reset(Fpga)
	logging.debug("done.")

	# Done with device
#	logging.debug("Closing device...")
	riffa.fpga_close(Fpga)
#	logging.debug("done.")
	
#=============================================================
# Send data to riffa PCIe devices
def PCIeSend(DataSend, Fpga, Channel, TimeOut=0):
	logging.info("Sending '{0}'".format([i for i in DataSend]))
	Sent = riffa.fpga_send(Fpga, Channel, DataSend, len(DataSend), 0, True, timeout=TimeOut)
#	logging.debug("done.")
	logging.info("Data sent: {0}/{1} (32bit words)".format(Sent, len(DataSend)))
	return Sent
	
#=============================================================
# Receive data from riffa PCIe devices
def PCIeReceive(NbData, Fpga, Channel, TimeOut=0):
	logging.debug("Receiving...")
	DataRecv = array.array('I', [0 for i in range(NbData)])
	Recv = riffa.fpga_recv(Fpga, Channel, DataRecv, timeout=TimeOut)#, ctypes.byref(TimeOut))
	if Recv>0:
#		OutputString="\n ".join(["{0:08x} ({0}d)".format(i) for i in DataRecv])
		logging.info("Data received: {0}".format([i for i in DataRecv[:Recv]]))
	logging.info("Received: {0} (32bit words)".format(Recv))
	return Recv
		
#=============================================================
def SendBinary(FileList, ID, Channel, TimeOut=0):
	Sent=0
	for FilePath in FileList:
		logging.debug("> FilePath  :".format(FilePath))
#			TypeDict={1:'b', 2:'h', 4:'i', 8:'q'}
		logging.debug("Open FPGA {0}, Channel {1}".format(str(ID), Channel))
		Fpga = riffa.fpga_open(ID)
		IntList=[]
		DataSend=None
		with open(FilePath, 'rb') as BinFile:
			while 1:
				ReadBytes=BinFile.read(4) # Read 4 bytes (32bit)
				if ReadBytes:
					ReadInt=struct.unpack('i', ReadBytes)[0]
#					logging.debug(' {0}'.format(ReadBytes))
					IntList.append(ReadInt)
					DataSend = array.array('I', IntList)
#					PCIeReceive(NbData=1, Fpga=Fpga, Channel=Channel, TimeOut=TimeOut)
				else:
					break
		if DataSend is None: 
			logging.warning("Nothing to send.")
		else:
			Sent+=PCIeSend(DataSend, Fpga=Fpga, Channel=Channel, TimeOut=TimeOut)
		logging.debug("End of file '{0}'.".format(os.path.basename(FilePath)))
	logging.info("Total data sent: {0}".format(Sent))
	logging.debug("Closing FPGA {0}...".format(ID))
	riffa.fpga_close(Fpga)
	logging.debug("Done.")

#=============================================================
def SendValues(Values, ID, Channel, TimeOut=0):
	"""
	Send values given as command arguments.
	"""
	logging.debug("> Values  : {0}".format(Values))
#	TypeDict={1:'b', 2:'h', 4:'i', 8:'q'}
	logging.debug("Open FPGA {0}, Channel {1}".format(str(ID), Channel))
	Fpga = riffa.fpga_open(ID)
	DataSend = array.array('I', Values)
#	PCIeReceive(NbData=1, Fpga=Fpga, Channel=Channel, TimeOut=TimeOut)
	Sent=PCIeSend(DataSend, Fpga=Fpga, Channel=Channel, TimeOut=TimeOut)
	logging.info("Total data sent: {0}".format(Sent))
#	logging.debug("Closing FPGA {0}...".format(ID))
	riffa.fpga_close(Fpga)
	logging.debug("Done.")
	
#=============================================================
def DumpBinary(FilePath, WordSize):
	logging.debug("Word size : {0}".format(WordSize))
	logging.debug("FilePath  : {0}".format(FilePath))

	TypeDict={1:'b', 2:'h', 4:'i', 8:'q'}
	Type=TypeDict[WordSize]
	with open(FilePath, 'rb') as BinFile:
		while 1:
			ReadBytes=BinFile.read(WordSize)
			if ReadBytes:
				ReadInt=struct.unpack(Type, ReadBytes)[0]
				print("{0}".format(ReadInt)+'({0})'.format(ReadBytes))
			else:
				break
	logging.debug("End of file '{0}'.".format(os.path.basename(FilePath)))
	
#====================================================================
def ConfigureFPGA(BitstreamPath):
	"""
	Remove current PCIe riffa module and Load FPGA with bitstream given as argument.
	"""
	logging.debug("Remove PCIe device '0000:01:00.0' ")
	os.system('sudo sh -c "echo 1 > /sys/bus/pci/devices/0000:01:00.0/remove"')
	
	logging.info("Program FPGA with xc3sprog")
	Cmd='xc3sprog -c jtaghs1_fast -v -p 0 {0}'.format(BitstreamPath)
	# Load the FPGA
	logging.debug(">"+Cmd)
	os.system(Cmd)
	ScanFpga()
	ReloadRiffaDriver()
	logging.debug("Done.")
	
	return 

#====================================================================
def ParseOptions():
	"""
	Parse argument options and do corresponding actions.
	"""
	Parser = argparse.ArgumentParser(description="Perform PCIe operations with FPGA Riffa devices.", epilog="")
	
	SubParsers = Parser.add_subparsers(dest="SubCommand", help='Any in [List, Reset, Send, Config, Loopback].')
	SubParsers.required = True

	# SUBCOMMANDS:
	ListCMD     = SubParsers.add_parser('List', help='List available FPGA.')
	ResetCMD    = SubParsers.add_parser('Reset', help='Reset FPGA with given ID.')
	SendFCMD    = SubParsers.add_parser('SendFile', help='Send content of binary file.')
	SendVCMD    = SubParsers.add_parser('SendValues', help='Send values given as arguments (32 bit words).')
	ReceiveCMD  = SubParsers.add_parser('Receive', help='Reset FPGA with given ID.')
	ConfigCMD   = SubParsers.add_parser('Config', help='download a design to FPGA (default: reference design). Use the xc3sprog program.')
	LoopbackCMD = SubParsers.add_parser('Loopback', help='Send/receive 200 32bit words.')
	DumpCMD     = SubParsers.add_parser('Dump', help='print content of a binary file.')

	#---------
	def FileTestFunc(F): 
		if not os.path.isfile(F): raise("No such file '{0}'").format(F) 
		else: return os.path.abspath(os.path.normpath(F))
	#----------SubCommand arguments-----------
	ListCMD.add_argument('--reload', action='store_true', help='Reload driver before listing devices.', default=False)
	#------
	ResetCMD.add_argument('id', metavar='ID', action='store', type=int, help='FPGA ID.')
	#------
	SendFCMD.add_argument("file", metavar='FilePath', action='append', type=FileTestFunc, help='One or more paths to binary files.')
	SendFCMD.add_argument("-i", "--id", metavar='ID', action='store', type=int, required=False, help='FPGA ID.', default=0)
	SendFCMD.add_argument("-c", "--channel", metavar='Channel', action='store', type=int, required=False, help='Riffa channel.', default=0)
	SendFCMD.add_argument("-t", "--timeout", metavar='TimeOut', action='store', type=int, required=False, help='Timeout (in sec).', default=2000)
	#------
	SendVCMD.add_argument("-v", "--values", metavar='Values', action='store', type=str, help='One or more integer (32bit) values to be sent.')
	SendVCMD.add_argument("-i", "--id", metavar='ID', action='store', type=int, required=False, help='FPGA ID.', default=0)
	SendVCMD.add_argument("-c", "--channel", metavar='Channel', action='store', type=int, required=False, help='Riffa channel.', default=0)
	SendVCMD.add_argument("-t", "--timeout", metavar='TimeOut', action='store', type=int, required=False, help='Timeout (in sec).', default=2000)
	#------
	ReceiveCMD.add_argument("-n", "--nbdata", metavar='NbData', action='store', type=int, required=True, help='Number of data to be received.')
	ReceiveCMD.add_argument("-i", "--id", metavar='ID', action='store', type=int, required=False, help='FPGA ID.', default=0)
	ReceiveCMD.add_argument("-c", "--channel", metavar='Channel', action='store', type=int, required=False, help='Riffa channel.', default=0)
	ReceiveCMD.add_argument("-t", "--timeout", metavar='TimeOut', action='store', type=int, required=False, help='Timeout (in sec).', default=2000)
	#------
	ConfigCMD.add_argument("file", metavar='FilePath', action='store', type=FileTestFunc, help='Path to a bitstream file.')
	#------
	LoopbackCMD.add_argument("-i", "--id", metavar='ID', action='store', type=int, required=False, help='FPGA ID.', default=0)
	LoopbackCMD.add_argument("-c", "--channel", metavar='Channel', action='store', type=int, required=False, help='Riffa channel.', default=0)
	LoopbackCMD.add_argument("-n", "--nbint", metavar='NbInt', action='store', type=int, required=False, help='Number of integer to be sent and received.', default=200)
	LoopbackCMD.add_argument("-t", "--timeout", metavar='TimeOut', action='store', type=int, required=False, help='Timeout (in ms).', default=2000)
	LoopbackCMD.add_argument("--soc", metavar='SoCFile', action='store', type=str, required=True, help='*.soc file associated with a SyntheSys generated design.')
	#------
	DumpCMD.add_argument("-f", "--file", metavar='FilePath', action='store', type=FileTestFunc, required=True, help='Paths to a binary file.')
	DumpCMD.add_argument("-w", "--wordsize", metavar='WordSize', action='store', type=int, required=False, help='Number of 32bit words in FPGA input.', default=4)
	#------
	
	Parser.set_defaults( func=Manage )
#	argcomplete.autocomplete(Parser)
	Args = Parser.parse_args()
	Args.func(Args)
		
#====================================================================
def Manage(Args):
	#---------------------------------------
	# List available FPGAs

	if Args.SubCommand=='List':
		if Args.reload is True:
			ReloadRiffaDriver()
		ScanFpga()
		ListFpga()
	#---------------------------------------
	elif Args.SubCommand=='Reset':
		# RESET FPGA 0
		ScanFpga()
		ResetFpga(Args.id)
	#---------------------------------------
	elif Args.SubCommand=='Config':
		BitstreamPath=Args.file
		ConfigureFPGA(BitstreamPath)
		ScanFpga()
		ListFpga()
	#---------------------------------------
	elif Args.SubCommand=='SendFile':
		SendBinary(FileList=Args.file, ID=Args.id, Channel=Args.channel, TimeOut=Args.timeout)
	#---------------------------------------
	elif Args.SubCommand=='SendValues':
		SendValues(Values=[int(x) for x in Args.values.split(',')], ID=Args.id, Channel=Args.channel, TimeOut=Args.timeout)
	#---------------------------------------
	elif Args.SubCommand=='Receive':
		logging.debug("Open FPGA {0}, Channel {1}.".format(str(Args.id), Args.channel))
		Fpga = riffa.fpga_open(Args.id)
		PCIeReceive(NbData=Args.nbdata, Fpga=Fpga, Channel=Args.channel, TimeOut=Args.timeout)
#		logging.debug("Closing...")
		riffa.fpga_close(Fpga)
		logging.debug("Done.")
	#---------------------------------------
	elif Args.SubCommand=='Loopback':
		ComAddress=GetNodeAddressFromCoord(Args.ComAddress)
		TestVector=list(range(15))
		DataSend = array.array('I', [ComAddress, len(TestVector)]+TestVector)
		DataRecv = array.array('I', len(TestVector)+2)
		
		Sent    = 0
		Recv    = 0
	
		ScanFpga()
#		logging.debug("Open FPGA", str(Args.id)+',', "Channel", Args.channel)
		Fpga = riffa.fpga_open(Args.id)
#		logging.debug("Fpga:", Fpga)
		Sent=PCIeSend(DataSend, Fpga=Fpga, Channel=Args.channel, TimeOut=Args.timeout)
	#	riffa.fpga_send(Fpga, Channel, Data, 100, 0, True, 5)
		if (Sent != 0):
			PCIeReceive(NbData=Args.nbint, Fpga=Fpga, Channel=Args.channel, TimeOut=Args.timeout)
		else:
			logging.warning("Nothing sent.")
		logging.debug("Closing...")
		riffa.fpga_close(Fpga)
		logging.debug("Done.")
	#---------------------------------------
	elif Args.SubCommand=='Dump':
		DumpBinary(FilePath=Args.file, WordSize=Args.wordsize)

	else:
		logging.error("COMMAND ERROR")
		sys.exit(1)



ParseOptions()
logging.debug("Exiting.")















