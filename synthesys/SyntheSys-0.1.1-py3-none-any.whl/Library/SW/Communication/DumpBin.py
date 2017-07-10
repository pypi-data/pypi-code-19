import array
import sys, os, struct, logging
import argparse

logging.basicConfig(filename=None, format='%(levelname)s: %(message)s', level=logging.INFO)

	
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
				print("{0}\t".format(ReadInt)+'({0})'.format('0x'+format(ReadInt, '0'+str(WordSize)+'X')))
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
	
	#---------
	def FileTestFunc(F): 
		if not os.path.isfile(F): raise("No such file '{0}'").format(F) 
		else: return os.path.abspath(os.path.normpath(F))
	#----------SubCommand arguments-----------
	Parser.add_argument("-f", "--file", metavar='FilePath', action='store', type=FileTestFunc, required=True, help='Paths to a binary file.')
	Parser.add_argument("-w", "--wordsize", metavar='WordSize', action='store', type=int, required=False, help='Number of 32bit words in FPGA input.', default=4)
	#------
	
	Parser.set_defaults( func=Manage )
#	argcomplete.autocomplete(Parser)
	Args = Parser.parse_args()
	Args.func(Args)
		
#====================================================================
def Manage(Args):
	#---------------------------------------
	# List available FPGAs
	DumpBinary(FilePath=Args.file, WordSize=Args.wordsize)



ParseOptions()















