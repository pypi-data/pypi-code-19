#! python3
import base64
import struct

def ascii85(ByteData):
	for x in range(4 - len(ByteData)):
		ByteData += b'\x00'
	print (ByteData)
	value=int.from_bytes(ByteData,byteorder='big', signed=False)
	return Base85(value)
def Base85(value):
	y = BaseX(value, 85)
	print (y)
	s = ""
	for x in y:
		s += chr(x + 33)
	return s

def BaseX(value, base=85):
	y = []
	#z = []
	remainder = value%base
	value = value//base
	y += [remainder]
	#print ("value:",value," remainder:",remainder)
	while value:
		#z += [value]
		remainder = value%base
		value = value//base
		y += [remainder]
		#print ("value:",value," remainder:",remainder)
		if value == 0 :
			break
	for i in range(5 -len(y)):
		y += [0]
		pass
	return list( reversed(y) )

v=16
S = struct.pack('>i',v)
print ("%s"%S)
#print (ascii85(S))
#print (base64.a85encode(S))
