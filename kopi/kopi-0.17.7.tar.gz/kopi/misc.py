__all__ =[	"itos","ftos", "ftos6",
			"Print", "PrintError", "PrintFatalError",
			"DecimalToAsciiHex",
			"InsertEscapeBeforeParenthesis",
			"BreakParagraphIntoLines",
			"BreakStringIntoSegments",
			"RemoveJsonComment",
			"Drink",
			"Decimal_To_10_DigitsString",
			"mm_to_pt",
			"ToPt",
			"GetPaperSize",
			"ThereIsListOrArrayWithinList",
			"IsListOrArray"]
from .myfont import *
import numpy as np

def itos (Int_Value):
		return "%d" %Int_Value

def ftos2 (Float_Value):
	S= "%.2f" %Float_Value
	n = len(S)
	if S[ n-3 : n ] ==".00":
		S = S[ 0 : n-3 ]
	elif (S [n -3 ] == ".") & (S [n-1] == "0"):
		S = S[ 0 : n-1]
	return S

def ftos6(FloatValue):
	Precision=6
	S= "%.6f" %FloatValue
	n = len(S)
	if S[n-1-Precision] == '.' :
		for m in range(Precision):
			n = len(S)
			if S[n-1] == "0":
				S = S[0:n-1]
			else:
				break
	if S[len(S)-1] =='.':
		S = S[0 : len(S)-1 ]
	return S

def ftos (Float_Value):
	#========================================================================
	# Instead of using python's ftos(), use this one to control the precision
	# my Float to String mini function
	# Remark:
	# One Postscript Point is 0.35278 mm (1/72 inch)
	# 0.01 Postscript Point is 0.0035 mm, which is about 3 micron !!
	# PyPlot seems to uses %.3f (300 nm ?)
	# Previously, the Floating Precision for Postscript Drawing Unit (Point)
	# was HardCoded to %.2f
	# Now, the default Float to String  precision is set to %.4f.
	S= "%.4f" %Float_Value
	n = len(S)
	if S[n-5] == '.' :
		if S[ n-4 : n ] =="0000":
			S = S[ 0 : n-5 ]
		elif S[n-3:n] == "000":
			S = S[ 0 : n-3]
		elif S[n-2:n] == "00":
			S = S[ 0 : n-2]
		elif S[n-1] == "0":
			S = S[ 0 : n-1]
	return S

def Print(S, show=False):#{{{
	if show:
		print(S)
	return#}}}

#Print error message with some fancy color
def PrintError(S, show=False):#{{{
	if show:
		red = "\33[1;31;40m"
		white = "\33[1;37;40m"
		print (red + "Error: " + white + S)
	return#}}}

#This one does not read the print option in the json file
def PrintFatalError(S):#{{{
	red = "\33[1;31;40m"
	white = "\33[1;37;40m"
	print (red + "Fatal Error: " + white + S)
	return#}}}

# Return TWO char HEX value in Ascii
# will become handy to generate value for
#pdf's AsciiHexDecode
def DecimalToAsciiHex(decimal):
	S = "%x"%decimal
	if len(S) ==1:
		S = "0" + S
	return S

def InsertEscapeBeforeParenthesis(Text):
	SplitText=Text.split(")")
	for n in range(len(SplitText)-1):
		SplitText[n] += "\\)"
	Result="".join(SplitText)

	SplitText=Result.split("(")
	for n in range(len(SplitText)-1):
		SplitText[n] += "\\("
	Result="".join(SplitText)
	return Result

# In the future, hopefuly Knuth algorithm can be implemented !
def BreakParagraphIntoLines(LongString, Xmax, FontName, FontSize):
	#{{{
	StringArray=LongString.split()
	NumberOfWords = len(StringArray)
	LengthOfEachWord= [0] * (NumberOfWords+1)
	#allocate one extra dummy to indicate the end off paragrah in the for loop

	for i in range (NumberOfWords):
		LengthOfEachWord[i] = GetStringWidth( StringArray[i] , FontName, FontSize)

	ContentInTheLine = [""]
	x=0
	l=0
	SpaceWidth =  GetFontWidth(32, FontName, FontSize)
	for i in range(NumberOfWords):
		ContentInTheLine[l] += (StringArray[i])
		x += LengthOfEachWord[i]
		if x + LengthOfEachWord[i+1] + SpaceWidth  > Xmax:
			x = 0
			ContentInTheLine +=[""]
			l+= 1
		else:
			ContentInTheLine[l] += " "
			x+= SpaceWidth
	return ContentInTheLine #}}}

def BreakStringIntoSegments(string):
	seg = []
	attri = []

	p=0	#initial or start after close bracket
	n=0	#open bracket index
	m=0	#close bracket index, or lastly, end of string
	n = string.find("{")
	while n !=-1:
		m = string.find("}", n+1)
		if string[n-1] == "_":
			if p!= n-1:
				seg.append( string[p : n-1]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("subscript")

		elif string[n-1]=="^":
			if p!= n-1:
				seg.append( string[p : n-1]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("superscript")

		elif string[n-2 : n]=="\L":
			if p!= n-2:
				seg.append( string[p : n-2]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("Large")

		elif string[n-2 : n]=="\l":
			if p!= n-2:
				seg.append( string[p : n-2]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("large")

		elif string[n-2 : n]=="\S":
			if p!= n-2:
				seg.append( string[p : n-2]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("Small")

		elif string[n-2 : n] =="\s":
			if p!= n-2:
				seg.append( string[p : n-2]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("small")

		elif string[n-2 : n]=="\i":
			if p!= n-2:
				seg.append( string[p : n-2]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("Italic")

		elif string[n-2 : n]=="\B":
			if p!= n-2:
				seg.append( string[p : n-2]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("Bold")

		elif string[n-3 : n ]=="\Bi":
			if p!= n-3:
				seg.append( string[p : n-3]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("BoldItalic")

		elif string.rfind("\c:", p , n) != -1:
			q = string.rfind("\c", p , n)
			color=string[q+3:n]
			if p!= q:
				seg.append( string[p : q]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("color:" + color)

		elif string.rfind("\R:", p , n) != -1:
			q = string.rfind("\R", p , n)
			angle=string[q+3:n]
			if p!= q:
				seg.append( string[p : q]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("rotate:" + angle)

		elif string.rfind("\F:", p , n) != -1:
			q = string.rfind("\F", p , n)
			newfont=string[q+3:n]
			if p!= q:
				seg.append( string[p : q]  )
				attri.append("normal")
			seg.append( string[n+1 : m]  )
			attri.append("font:" + newfont)

		else:
			if p!= n:
				seg.append( string[p : n]  )
				attri.append("normal")
			seg.append( string[n : m+1]  )
			attri.append("unknown")
		p=m+1
		lastfound = n
		n = string.find("{", n+1)

	if p <  len(string):
		seg.append( string[p:len(string)] )
		attri.append("normal")
	return [seg, attri]

def FindAll(String, Char):
    # The Python find Sucks.It only return first found result.
    # I need the following to find all.
    # But it turn out that, xxx.split() is much better. Sorry.
	Index=[]
	n=0
	Check =  String.find(Char, 0)
	while Check !=-1:
		Index.append( Check )
		n += 1
		Check = String.find(Char, Index[n-1] +1)
	return Index

def RemoveJsonComment(text):
	# Simple code to remove the comments start with "//"
	# in the json file.
	# It is like removing the C-style comments,
	# but not extended to handle "/* .....*/"
	lines = text.split("\n")
	S = ""
	for line in lines:
		if line.find("//") != -1:
			line = line[0:line.find("//")]
		if len(line) != 0:
			S += line +"\n"
	return S

def ThereIsListOrArrayWithinList( L):
	if not isinstance(L, list):
		return False
	for l in L:
		if isinstance(l, list) or isinstance(l, np.ndarray):
			return True
	return False

def IsListOrArray(L):
	if isinstance(L, list) or isinstance(L, np.ndarray):
		return True
	else:
		return False


def Drink(What, n):
	"""Drink(What, n):
	"What" can be scalar or array.
	If "What" is scalar, just return the value.
	If "What" is a list, return the n-th element.
	It is used for parameter that can accept both scalar or list.
	Usually it is used when handling single or
	multiple plots, say with different colors."""
	if isinstance(What,list) == False:
		return What
	else:
		if n> len(What) -1:
			Print("Repeat the plot style.")
			return  What[n%len(What)]
		else:
			return What[n]


def Decimal_To_10_DigitsString(value):
	Decimal = int(value) # just in case if user put something else.
	S = "%d"%Decimal
	AdditionalZerosd = "0" * (10- len(S) )
	return AdditionalZerosd + S

def mm_to_pt(milimeter):
	return 1.0*milimeter/0.3528


def ToPt( ValueSpecifiedInArbitraryUnit, Unit="pt"):
	if Unit=="pt":
		return ValueSpecifiedInArbitraryUnit
	elif Unit=="cm":
		return 28.3465*ValueSpecifiedInArbitraryUnit
	elif unit=="inch":
		return 72*ValueSpecifiedInArbitraryUnit
	else:
		return ValueSpecifiedInArbitraryUnit

def GetPaperSize(PaperSize, Unit="pt", Portrait=True):
	#Allow two input formats:
	#	eg.	PaperSize = "A4"
	#	or	PaperSize = [400, 500]
	#	return
	CommonPaperSizeByName = {
		"Letter"		:"612 792",
		"Tabloid"		:"792 1224",
		"Ledger"		:"1224 792",
		"Legal"			:"612 1008",
		"Statement"		:"396 612",
		"Executive"		:"540 720",
		"A0"			:"2384 3371",
		"A1"			:"1685 2384",
		"A2"			:"1190 1684",
		"A3"			:"842 1190",
		"A4"			:"595 842",
		"A5"			:"420 595",
		"B4"			:"729 1032",
		"B5"			:"516 729",
		"Folio"			:"612 936",
		"Quarto"		:"610 780",
		"10x14"			:"720 1008"
		}
	if isinstance(PaperSize, list)==True:
		if len(PaperSize) ==2:
			if Unit=="pt":
				return itos(int(PaperSize[0])) +\
					" " +\
					itos(int(PaperSize[1]))
			else:
				return ftos(ToPt(PaperSize[0],Unit)) +\
					" " +\
					ftos(ToPt(PaperSize[1],Unit))
		else:
			PrintError("Invalid Manual Paper Size Parameters." +
					" Assume Letter")
			return CommonPaperSizeByName["Letter"]

	else:
		if PaperSize in CommonPaperSizeByName:
			S = CommonPaperSizeByName[PaperSize]
			if Portrait == False:
				# assume landscape. Inverse the position for Paper Size
				S = S.split(" ")
				S = S[1] + " " + S[0]

			print(CommonPaperSizeByName[PaperSize])
			return S

		else:
			PrintError("Name Paper of Paper Size Not Valid. Asssume Letter")
			return CommonPaperSizeByName["Letter"]
