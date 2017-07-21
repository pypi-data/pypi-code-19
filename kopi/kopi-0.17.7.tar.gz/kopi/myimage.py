# To save my life time, I use the existing Image Processing Library
# PIL.
# Maintanence of orginal PIL is discontinued,
# so it could no longer be installed with pip.
# Use  PIL fork : Pillow instead
# e.g.:
# sudo easy_install pip
# sudo pip install pillow

__all__ = ["GetImageByteStreamFromData",
			"GetImageByteStreamFromFile",
			"IsJPGFile"]

from PIL import Image
from .misc import *
import zlib as gzip
import binascii

def IsJPGFile(Filename):
	if Filename[Filename.rfind('.'):len(Filename)] == ".jpg":
		return True
	else:
		return False

def GetImageByteStreamFromData(ImageData):
	#Data format: array of [[R,G,B], ...]
	# E.g.
	#ImageData=[[128,128,128],[128,128,128],[34,70,24],[67,34,90]]):
	imgS = ""
	for n in range(len(ImageData)):
		for m in range(3):
			imgS += DecimalToAsciiHex(round (ImageData[n][m]))
	imgS += ">" #End of Data
	imgS = imgS.encode()
	imgS = gzip.compress(imgS)
	return imgS

# use PIL to peek on the file
def GetImageByteStreamFromFile(ImageFilename, DCTDecode=False):
	try:
		fa = Image.open(ImageFilename)
		ImageWidth = fa.size[0]
		ImageHeight = fa.size[1]
	except:
		PrintError("Error Opening Image file !")
		return -1
	if DCTDecode & IsJPGFile(ImageFilename):
	#'Decompresses data encoded using a DCT
	#(discrete cosine transform) technique based on the JPEG standard,
	#reproducing image sample data that approximates the original data.'
	#from pdf reference 1.7
	# That mean I will just leave the jpg file as it is.
	# ANyway, need to hexilify the data.
		try:
			with open(ImageFilename, "rb") as fb:
				imgS = binascii.hexlify( fb.read())
				imgS += ">".encode()
		except:
			PrintError("Error Opening/Reading JPG file !")
			return -1
	else:
		imgD = list(fa.getdata())
		imgS = ""
		for n in range(len(imgD)):
			for m in range(3):
				imgS += DecimalToAsciiHex(imgD[n][m])
		imgS += ">" #End of Data
		imgS = imgS.encode()
	#Finish
	imgS = gzip.compress(imgS)
	return [imgS, ImageWidth, ImageHeight]
