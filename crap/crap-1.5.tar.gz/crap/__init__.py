'''
INFO
--------

Name: Crap File Format
Description: Encodes and decodes files in .crap format. This allows one to execute the file in any languge, immediately upon import.
Version: 1.0
Created by: Nirman Dave
'''

def decode(file_location):
	'''
	Decodes a crap file and executes it
	'''
	if file_location[-5:] == ('.crap'):
		crap_reader = open(file_location, 'r')
		crap_seen = crap_reader.read()
		crap_reader.close()
		crap_data = eval(crap_seen)
		return crap_data
	else:
		raise NameError('File needs to be encoded as .crap')

def encode(data, file_location):
	'''
	Encodes data into an executable .crap file
	'''

	cdata = str(data)

	crap_writer = open(file_location, 'w')
	crap_writer.write(cdata)
	crap_writer.close()