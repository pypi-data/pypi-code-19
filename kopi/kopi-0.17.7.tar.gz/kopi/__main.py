"""
	Main module to plot graph
"""
__all__ = ["plot", "image","polar","mplot"]
import sys
import numpy as np
#import json
import math

# Yet complete:
# Allow the Axes Line to be drawn starting at the 0,0 origin
# Axis lines -> Done, but tick position -> not yet
#Problem:
#The display values not stable when dealt with large value like
# y x 10^21

from . import myglobal
from .brewcson import *
from .myfont import *
from .mycolor import *
from .mypretty import *
#from . import pdf #I like to keep the pdf namespace
#from . import htmlcanvas as pdf
from .misc import *
from .myimage import *
from .mycson import *
# Try to add features to  Formated Text. e.g color, rotation , etc.


def loadtxt(Filename):
	#simple loadtxt to auto detect the skiprows
	#and return in X,Y
	def IsAllElementInListAreFloat(StringList):
		ans = True
		for s in StringList:
			try :
				float(s)
				#if ok, then do nothing
			except:
				ans = False
				return ans
		return ans
	def GetSkipRowsAndDelimiter(Filename):
		# Try to scan the first few lines to search for the start line
		# for valid data.
		# Assume the delimiter is "," or "\t" or " "
		# PS. It does not scan the whole data !
		f = open(Filename,'r')
		n = 0
		while n<1000:
			try:
				s = f.readline()
				#print s.rstrip("\n")
				#replace "\t" and " " with ",", then split the line
				SplitElement =  s.\
					replace(",\t",",").\
					replace(", ",",").\
					replace('\t',",").\
					replace("    ",",").\
					replace("  ",",").\
					replace(" ",",").\
					rstrip("\n").\
					split(",")
				if IsAllElementInListAreFloat(SplitElement):
					break
				if s=="":
					#if there is nothing, not even "\n", then break
					n= -1
					break
				n += 1
			except:
				print ("can not readline")
				return -1
		S=f.readline()
		Delimiter = ","	if "," in S else ""
		f.close()
		return n, Delimiter
	SkipRows,Delimiter = GetSkipRowsAndDelimiter(Filename)
	print("Number of Line to be skipped: ", SkipRows)
	print("Delimiter: ", [Delimiter])
	if Delimiter==",":
		Data = np.loadtxt(Filename, skiprows = SkipRows,
		delimiter = Delimiter)
	else:
		Data = np.loadtxt(Filename, skiprows = SkipRows)


	X=Data[:,0]
	Y=Data[:,1]
	return X,Y

def GenerateMinorTicks(MajorTick = [], TickNumber = 5, log = False):
	MinorTick = np.array([])
	if log == False:
		# e.g. For Major tick, [0, 1, 2]
		# generate
		# [0, 0.2, 0.4, 0.6, ...1, 1.2 ...2]
		spacing =  1.0*(MajorTick[1] - MajorTick[0])/TickNumber
		for i in range(len(MajorTick) -1):
			temp = MajorTick[i]
			for j in range(TickNumber):
				temp = temp + spacing
				MinorTick=np.append(MinorTick, temp)

	else:
		# e.g. For Major tick, [0.1, 1, 10, 100 ]
		# generate a list like this one for Log plot
		#[0.1, 0.2, 0.4, 0.6,0.8,1, 2, 4, 6, 8, 10, 20, 40 ...]
		spacing = (MajorTick[1]/MajorTick[0]) / TickNumber
		for i in range(len(MajorTick) -1):
			temp =	MajorTick[i]
			for j in range(TickNumber):
				if j ==1:
					temp = spacing*MajorTick[i]
				if j > 1:
					temp = temp + spacing*MajorTick[i]
				MinorTick=np.append(MinorTick, temp)

	return MinorTick

FontHeightRatio = 0.7
SuperScript_FontSizeReduction = 4
Superscript_YoffsetRatio = 0.8
Subscript_FontSizeReduction = 4
Subscript_YoffsetRatio = 0.5
FontSizeEnlargementStep = 2
KeepFontSize = True




def PDF_ObjForAllPages(OffsetNum, NumOfPage):
	S=""
	for i in range(NumOfPage):
		S+= str(OffsetNum + 2*i) + " 0 R "
	return S

# Make Multipages pdf.
# Each element in the GS stream vector is drawn in that
# particular page.
def MakeMultiplePDF(GraphicsStream, Compress=True):
	#{{{
	NumOfPage = len(GraphicsStream)
	if Compress==True:
		for i in range(NumOfPage):
			GraphicsStream[i]=gzip.compress(GraphicsStream[i])

	NumOfBasicObj = 21
	NumberOfPageObject = NumOfPage*2

	pdf_objects = []
	pdf_objects.append(
			"%PDF-1.4\n"+
			"% Created Manually\n"+
			"%%Creator: Lee Chuin CHEN\n" +
			"%% [leechuin@yamanashi.ac.jp, leechuin@gmail.com]\n" +
			"%%Title: Plot\n" +
			"%%CreationDate: "+ str(datetime.now()) + "\n"
			)

	pdf_objects.append(
			"1 0 obj\n"+
			"<</Type /Catalog\n" +
			"/Outlines 2 0 R\n" +
			"/Pages 3 0 R\n" +
			">>\n" +
			"endobj\n"
			)

	pdf_objects.append(
			"2 0 obj\n" +
			"<</Type /Outlines\n" +
			"/Count 0\n" +
			">>" +
			"endobj\n"
			)

	ObjOffsetNumber= 40

	pdf_objects.append(
			"3 0 obj\n" +
			"<</Type /Pages\n" +
			"/Kids ["+
			PDF_ObjForAllPages(ObjOffsetNumber, NumOfPage) +
			"]\n" +
			"/Count "+ str(NumOfPage) +"\n" +
			">>\n" +
			"endobj\n"
			)
	pdf_objects.append(
			"4 0 obj\n"+
			"<<"+
			"/Producer (Univ. Yamanashi)" +
			">>"+
			"endobj\n"
			)

	pdf_objects.append(
			"5 0 obj\n"+
			"<<"+
			"/Creater (LCCHEN))" +
			">>"+
			"endobj\n"
			)

	pdf_objects.append(
			"6 0 obj\n" +
			"[/PDF /Text]\n"+
			"endobj\n"
			)

	pdf_objects.append(
			pdf.DefineFont(7, 0, fontname.Helvetica, "FH")
			)
	pdf_objects.append(
			pdf.DefineFont(8, 0, fontname.Helvetica_Bold, "FHB")
			)
	pdf_objects.append(
			pdf.DefineFont(9, 0, fontname.Helvetica_Oblique, "FHO")
			)
	pdf_objects.append(
			pdf.DefineFont(10, 0, fontname.Helvetica_BoldOblique, "FHBO")
			)
	pdf_objects.append(
			pdf.DefineFont(11, 0, fontname.Times_Roman, "FT")
			)
	pdf_objects.append(
			pdf.DefineFont(12, 0, fontname.Times_Italic, "FTI")
			)
	pdf_objects.append(
			pdf.DefineFont(13, 0, fontname.Times_Bold, "FTB")
			)
	pdf_objects.append(
			pdf.DefineFont(14, 0, fontname.Times_BoldItalic, "FTBI")
			)

	if PlotOnlyForAdobeIllustrator == True:
		pdf_objects.append(pdf.DefineFont(15,
				0,
				"SymbolMT",
				"FS") #For Illustrator, but can not open even with Adobe Reader
				)
	else:
		pdf_objects.append(
				pdf.DefineFont(15, 0, "Symbol", "FS") # Common
				)

	pdf_objects.append(
			pdf.DefineFont(16, 0, fontname.Symbol_ZapfDingbats, "FSZ")
			)
	pdf_objects.append(
			pdf.DefineFont(17, 0, fontname.Courier, "FC")
			)
	pdf_objects.append(
			pdf.DefineFont(18, 0, fontname.Courier_Bold, "FCB")
			)
	pdf_objects.append(
			pdf.DefineFont(19, 0, fontname.Courier_Oblique, "FCO")
			)
	pdf_objects.append(
			pdf.DefineFont(20, 0, fontname.Courier_BoldOblique, "FCBO")
			)

	for n in range(NumOfPage):
		pdf_objects.append(
			str(ObjOffsetNumber + 2*n) +
			" 0 obj\n" +
			"<</Type /Page\n" +
			"/Parent 3 0 R\n" +
			"/MediaBox [0 0 612 792]\n" +
			"/Contents " +
			str(ObjOffsetNumber + 2*n + 1) +
			" 0 R\n" +
			"/Resources<</ProcSet 6 0 R\n" +
			"/Font <<	/FH 7 0 R\n" +
			"		/FHB 8 0 R\n"+
			"		/FHO 9 0 R\n"+
			"		/FHBO 10 0 R\n"+
			"		/FT 11 0 R\n" +
			"		/FTI 12 0 R\n" +
			"		/FTB 13 0 R\n" +
			"		/FTBI 14 0 R\n" +
			"		/FS 15 0 R\n" +
			"		/FSZ 16 0 R\n" +
			"		/FC 17 0 R\n" +
			"		/FCB 18 0 R\n" +
			"		/FCO 19 0 R\n" +
			"		/FCBO 20 0 R\n" +
			">>\n"+
			">>\n"+
			">>\n"+
			"endobj\n"
			)

		StreamObj= (
			str(ObjOffsetNumber + 2*n + 1) +
			" 0 obj\n" +
			"<< /Length %d "%len(GraphicsStream[n])
			)
		if Compress ==True:
			StreamObj +=  "/Filter /FlateDecode"

		StreamObj +=  (
			">>\n"+
			"stream\n" +
			GraphicsStream[n] + "\n"+
			"endstream\n"+
			"endobj\n"
			)
		pdf_objects.append(StreamObj)


	NumOfPdfObj=NumOfBasicObj + 2*NumOfPage
	offset = [0]*(NumOfPdfObj)
	for i in range(1, NumOfPdfObj):
		offset[i] = offset[i-1] + len(pdf_objects[i-1])
	startxref = offset[NumOfPdfObj-1] + len(pdf_objects[NumOfPdfObj-1])

	Xref_0=""
	for i in range(1 , NumOfBasicObj):
		Xref_0 += Decimal_To_10_DigitsString(offset[i]) + " 00000 n\r\n"

	Xref_1=""
	for i in range(NumOfBasicObj, NumOfPdfObj):
		Xref_1 += Decimal_To_10_DigitsString(offset[i]) +\
				" 00000 n\r\n"

	pdf_xref = (
		"xref\n"+
		"0 "+ str(NumOfBasicObj) +" \r\n"+
		"0000000000 65535 f\r\n"+
		Xref_0 +
		str(ObjOffsetNumber) + " " + str(2*NumOfPage) + "\r\n"+
		Xref_1 +
		"trailer\n"+
		"<</Size 8\n"+
		"/Root 1 0 R\n"+
		">>\n"+
		"startxref\n"+
		"%d"%(startxref) + "\n"
		"%%%EOF\n"
		)

	TargetFile = open(cafe["PDF"]["PDF_Filename"],"w")

	for X in pdf_objects:
		TargetFile.write(X)

	TargetFile.write(pdf_xref)
	TargetFile.close()
	os.system(cafe["PDF"]["PDF_Viewer"] +" "+ cafe["PDF"]["PDF_Filename"])
	return#}}}

def GetMinMaxForXYarray(XList, YList):
	"""GetMinMaxForXYarray(XList, YList):
	Return [xmin, xmax], [ymin, ymax]
	eg.	x = [ [1,2,3,6], [0,1,2] ]
		y = [ [-2, 2,3,4], [1, 2, 6]
	the return values are [0, 6], [-2, 6]
	"""
	if isinstance(YList, list) != True:
		PrintError("Ydata is not a list")
		raise Exception("Ydata is not a valid list")
	if isinstance(XList, list) !=True:
		PrintError("Xdata is not a list like Ydata.!")
		raise Exception("Xdata is not a valid list")
	if len(XList) != len(YList):
		PrintError("The number of array for X and Y does not match !")
		raise Exception("Number of array does not match")
	Xmin = min(XList[0])
	Xmax = max(XList[0])
	Ymin = min(YList[0])
	Ymax = max(YList[0])
	for n in range(len(YList)):
		xa = XList[n]
		ya = YList[n]
		if len(ya) != len(xa) :
			PrintError("The Numbers of element in X and Y are not equal");
			raise Exception("Dimension for X and Y are not the same")
		if min(xa)< Xmin:
			Xmin = min(xa)
		if max(xa)> Xmax:
			Xmax = max(xa)
		if min(ya)< Ymin:
			Ymin = min(ya)
		if max(ya)> Ymax:
			Ymax = max(ya)
	return [Xmin, Xmax, Ymin, Ymax]


def load_cafe_as_global(coffee, sugar):
	global cafe
	global Origin
	global Width
	global Height

	try:
		check = open(coffee,"r")
		check.close()
	except:
		print(	"Can't find ", coffee, ".\n",
				"I will create one for you.\n")
		brew_cson(coffee)


	#try:
	cafe = loadcsonfile(coffee)
	if len(sugar) !=0:
		#found that it is equivalent to sugar.keys()
		for x in sugar:
			if isinstance(sugar[x], dict):
				for y in sugar[x]:
					if isinstance(sugar[x][y], dict):
						for z in sugar[x][y]:
							a[x][y][z] =\
							 sugar[x][y][z]
					else:
						a[x][y] = sugar[x][y]
			else:
				a[x]=sugar[x]
	if cafe["Debug"]["EchoThisContent"]==True :
		PrintDictContent(a)
	Origin = cafe["PlotRange"]["Origin"]
	Width = cafe["PlotRange"]["Width"]
	Height = cafe["PlotRange"]["Height"]

	global pdf
	if cafe["PDF"]["UseHTMLCanvas"]:
		from . import htmlcanvas as pdf
	else:
		from . import pdf as pdf

	pdf.ResetPDF_FilenameNumber()
	pdf.Initialize(paperheight=cafe["Paper"]["Size"][1])
	return 0

def load_b_as_global(morecoffee, milk):
	#{{{
	global b
	global OverallOrigin
	global OverallWidth
	global OverallHeight
	#try:

	try:
		check = open(morecoffee,"r")
		check.close()
	except:
		print(	"Can't find multiplotstyle.cson file.\n",
				"I will create one for you.\n")
		create_multiplot_cson(morecoffee)

	b=loadcsonfile(morecoffee)
	if len(milk) !=0:
		#found that it is equivalent to sugar.keys()
		for x in milk:
			if isinstance(milk[x], dict):
				for y in milk[x]:
					if isinstance(milk[x][y], dict):
						for z in milk[x][y]:
							b[x][y][z] =\
							 milk[x][y][z]
					else:
						b[x][y] = milk[x][y]
			else:
				b[x]=milk[x]
	OverallOrigin = b["Origin"]
	OverallWidth = b["Width"]
	OverallHeight = b["Height"]
	return 0

	#except Exception as e:
	#	PrintFatalError("Exception in loading MultiPlot cson")
	#	print (e)
	#	return -1#}}}


def splot(DataXList, DataYList,
		SecondaryAxis = False,
		PlotAxesOnly = False,
		UpperError=[],
		LowerError=[]):
	"""Main function to create the pdf graphic script.
	Return 0 if successful, and -1 is not."""


	def pdf_DrawXtick():
		tickrgb = pdf.ToPSColor(cafe["Xaxis"]["Tick"]["Color"])
		textrgb = pdf.ToPSColor (cafe["Xaxis"]["Tick"]["FontColor"])
		XTickNumber = len(XTickArray_inPt)
		TextPosition_X = [0] * XTickNumber #create N elemetnts of 0

		TickDirection = 1.0 if cafe["Xaxis"]["Tick"]["TickOut"] else -1.0

		CorrectionForTickLength  = TickDirection*\
								cafe["Xaxis"]["Tick"]["Length"]
		if CorrectionForTickLength < 0:
			CorrectionForTickLength = 0

		yTextPositionOffset = -1.0* (
				CorrectionForTickLength +\
				1.0 * cafe["Xaxis"]["Tick"]["FontSize"])

		TextPosition_Y = [ Origin[1] +\
		 				yTextPositionOffset ] * XTickNumber
		TickText = [""] * XTickNumber

		for n in range(XTickNumber):
			TickText[n] = ftos6( XTickArray[n] )
			TextPosition_X[n] = XTickArray_inPt[n]

		# The following correction is needed to draw the tick line
		# so that it will appear to connect to the Axes lines of finite
		# linewidth.
		# eg:	==== Axis line
		# 		|  | Tick
		correction = cafe["Xaxis"]["LineWidth"]/2
		ReturnString =""
		ReturnString +=\
		 	pdf.DrawXTick(	[Origin[0], Origin[1] + correction ],
							XTickArray_inPt,
							TickDirection *\
							cafe["Xaxis"]["Tick"]["Length"] + correction,
							cafe["Xaxis"]["Tick"]["Width"],
							tickrgb)
		if cafe["Xaxis"]["ShowTickText"]==True:
			ReturnString += pdf.PutTextArray(
				TextPosition_X, TextPosition_Y,
				TickText, cafe["Xaxis"]["Tick"]["Font"],
				cafe["Xaxis"]["Tick"]["FontSize"],textrgb, 0, [0.5,0])

		return ReturnString

	def pdf_DrawMinorXtick():
		TickDirection = 1.0 if cafe["Xaxis"]["Tick"]["TickOut"] else -1.0
		S =""
		S += pdf.DrawXTick(
				Origin,
				MinorXTickArray_inPt,
				TickDirection*\
				MinorTickLength,
				cafe["Xaxis"]["MinorTick"]["LineWidth"],
				pdf.ToPSColor(cafe["Xaxis"]["MinorTick"]["LineColor"]))
		return S

	def pdf_DrawXgrid():
		gridlength = Height
		S =""
		S += pdf.DrawXTick(
				Origin,
				XTickArray_inPt,
				-1*gridlength,
				cafe["Xaxis"]["Grid"]["LineWidth"],
				pdf.ToPSColor(cafe["Xaxis"]["Grid"]["LineColor"]),
				pdf.ToPSDash(cafe["Xaxis"]["Grid"]["LineType"]))
		return S

	def pdf_DrawMinorXgrid():
		gridlength = Height
		S = pdf.DrawXTick(Origin, MinorXTickArray_inPt,
				-1*gridlength,
				cafe["Xaxis"]["MinorGrid"]["LineWidth"],
				pdf.ToPSColor(cafe["Xaxis"]["MinorGrid"]["LineColor"]),
				pdf.ToPSDash(cafe["Xaxis"]["MinorGrid"]["LineType"]))
		return S

	def pdf_DrawYtick():
		rgb = pdf.ToPSColor( cafe["Yaxis"]["Tick"]["Color"] )
		textrgb = pdf.ToPSColor (cafe["Yaxis"]["Tick"]["FontColor"])
		YTickNumber = len(YTickArray_inPt)
		TextPosition_Y = [0] * YTickNumber
		TextPosition_X = [0] * YTickNumber
		TickText = [""] * YTickNumber

		TickDirection = 1.0 if\
		 	cafe["Yaxis"]["Tick"]["TickOut"] else -1.0

		CorrectionForTickLength  = TickDirection*\
								cafe["Yaxis"]["Tick"]["Length"]
		if CorrectionForTickLength < 0:
			CorrectionForTickLength = 0

		for n in range(YTickNumber):
			TickText[n] = ftos6(YTickArray[n])
			xTextPositionOffset = -1.0*\
					(cafe["Yaxis"]["Tick"]["OffsetOfTextFromTickOverWidth"]*\
					cafe["PlotRange"]["Width"] +\
					CorrectionForTickLength)
			TextPosition_X[n] = Origin[0] + xTextPositionOffset
			yTextPositionOffset =\
			 	(1.0- FontHeightRatio)*cafe["Yaxis"]["Tick"]["FontSize"]
			TextPosition_Y[n] = (YTickArray_inPt[n] + yTextPositionOffset)
			if SecondaryAxis==True:
				xTextPositionOffset = 1.0* (2*cafe["Yaxis"]["Tick"]["Length"])
				TextPosition_X[n] = Origin[0] + Width + xTextPositionOffset

		# The following correction is needed to draw the tick line
		# so that it will appear to connect to the Axes lines of finite
		# linewidth.
		# eg:
		#		Tick	-|
		#		Axis	 |
		correction = cafe["Yaxis"]["LineWidth"]/2

		S =""
		if SecondaryAxis==False:
			S += pdf.DrawYTick(
				[Origin[0]+correction, Origin[1] ],
				YTickArray_inPt,
				TickDirection*\
				(cafe["Yaxis"]["Tick"]["Length"] + correction),
				cafe["Yaxis"]["Tick"]["Width"],
				rgb)
		else:
			S += pdf.DrawYTick(
				[Origin[0] + Width - correction,
					Origin[1] ],
				YTickArray_inPt,
				-1*TickDirection*\
				(cafe["Yaxis"]["Tick"]["Length"] + correction),
				cafe["Yaxis"]["Tick"]["Width"],
				rgb)


		if(cafe["Yaxis"]["ShowTickText"]==True):
			S += pdf.PutTextArray(TextPosition_X,
								TextPosition_Y,
								TickText,
								cafe["Yaxis"]["Tick"]["Font"],
								cafe["Yaxis"]["Tick"]["FontSize"],
								textrgb,
								0,
								([1, 0.5] #x:right justified
								if SecondaryAxis==False else
								[0, 0.5] #x:left justified
								 ),
								)
		return S

	def pdf_DrawMinorYtick():
		TickDirection = 1.0 if\
		 	cafe["Yaxis"]["Tick"]["TickOut"] else -1.0
		rgb = pdf.ToPSColor( cafe["Yaxis"]["MinorTick"]["LineColor"] )
		S = pdf.DrawYTick(Origin,
				MinorYTickArray_inPt,
				TickDirection *\
				MinorTickLength,
				cafe["Yaxis"]["MinorTick"]["LineWidth"],
				rgb)
		return S

	def pdf_DrawMinorYgrid():
		gridlength = Width
		S =""
		S += pdf.DrawYTick(
				Origin,
				MinorYTickArray_inPt,
				-1*gridlength,
				cafe["Yaxis"]["MinorGrid"]["LineWidth"],
				pdf.ToPSColor(cafe["Yaxis"]["MinorGrid"]["LineColor"]),
				pdf.ToPSDash(cafe["Yaxis"]["MinorGrid"]["LineType"]))
		return S

	def pdf_DrawYgrid():
		gridlength = Width
		S =""
		S += pdf.DrawYTick(
					Origin,
					YTickArray_inPt,
					-1*gridlength,
					cafe["Yaxis"]["Grid"]["LineWidth"],
					pdf.ToPSColor(cafe["Yaxis"]["Grid"]["LineColor"]),
					pdf.ToPSDash(cafe["Yaxis"]["Grid"]["LineType"]))

		return S

	def pdf_PutYlabel():
		#{{{
		if SecondaryAxis ==True:
			cafe["yLabel"]["Text"] = cafe["y2Label"]

		S = ""
		LongestYValue=str(max(YTickArray))
		rgb=pdf.ToPSColor(cafe["yLabel"]["FontColor"])
		if SecondaryAxis == False:
			textposition_x = (
				Origin[0] -
				cafe["Yaxis"]["Tick"]["Length"] -
				GetStringWidth(LongestYValue,
					cafe["Yaxis"]["Tick"]["Font"],
					cafe["Yaxis"]["Tick"]["FontSize"]) -
				cafe["yLabel"]["FontSize"] -
				cafe["yLabel"]["OffsetX"]
				)
		else:
			textposition_x = (
					Origin[0] +
					cafe["Yaxis"]["Tick"]["Length"] +
					Width +

					2.0*GetStringWidth(
						LongestYValue,
						cafe["Yaxis"]["Tick"]["Font"],
						cafe["Yaxis"]["Tick"]["FontSize"]) +
					cafe["yLabel"]["FontSize"] +
					cafe["yLabel"]["OffsetX"]
					)
		textposition_y = (Origin[1] +
							Height/2 +
							cafe["yLabel"]["OffsetY"])

		S += pdf.PutText(textposition_x,
							textposition_y,
							cafe["yLabel"]["Text"],
							cafe["yLabel"]["Font"],
							cafe["yLabel"]["FontSize"],
							rgb,
							90, [0.5,0])
		return S
		#}}}

	def pdf_PutXlabel():
		S = ""
		rgb=pdf.ToPSColor(cafe["xLabel"]["FontColor"])

		textposition_x = (	Origin[0]+
							0.5*Width  +
							1.0*cafe["xLabel"]["OffsetX"])

		TickDirection = 1.0 if cafe["Xaxis"]["Tick"]["TickOut"] else -1.0

		CorrectionForTickLength  = TickDirection*\
								cafe["Xaxis"]["Tick"]["Length"]
		if CorrectionForTickLength < 0:
			CorrectionForTickLength = 0


		textposition_y = Origin[1] -\
	 		1.0* (
					CorrectionForTickLength+\
			1.0*cafe["Xaxis"]["Tick"]["FontSize"] +\
			1.0*cafe["xLabel"]["FontSize"]+\
			1.0*cafe["xLabel"]["OffsetY"])
		S += pdf.PutText(textposition_x,
							textposition_y,
							cafe["xLabel"]["Text"],
							cafe["xLabel"]["Font"],
							cafe["xLabel"]["FontSize"],
							rgb,
							0, [0.5,0])
		return S

	def pdf_PutTitle():
		S =""
		if cafe["Title"]["Show"]:
			TitleLineNumber = len(BreakParagraphIntoLines(cafe["Title"]["Text"],
									TitleWidth,
									cafe["Title"]["Font"],
									cafe["Title"]["FontSize"]))
			y = (	Origin[1] +
				Height +
				cafe["Title"]["Yoffset"]*Height +
				cafe["Title"]["FontSize"]*cafe["Title"]["Spacing"]*\
					(TitleLineNumber-1)
				)
			if (cafe["Title"]["Alignment"]=="center") |\
			 	(cafe["Title"]["Alignment"]=="c"):
				pdf_TitleAlignment = 0.5
				x=Origin[0] + Width/2
			elif (cafe["Title"]["Alignment"]=="right") |\
			 		(cafe["Title"]["Alignment"]=="r"):
				pdf_TitleAlignment = 1
				x = Origin[0] +Width - cafe["Title"]["Xoffset"]*Width
			elif (cafe["Title"]["Alignment"]=="left") |\
			 		(cafe["Title"]["Alignment"]=="l"):
				pdf_TitleAlignment = 0
				x = Origin[0] + cafe["Title"]["Xoffset"]*Width
			else:
				pdf_TitleAlignment=0.5
				x=Origin[0] + Width/2
			S += pdf.Print(	cafe["Title"]["Text"],
						x,
						y,
						TitleWidth,
						cafe["Title"]["Font"],
						cafe["Title"]["FontSize"],
						pdf.ToPSColor(cafe["Title"]["FontColor"]),
						pdf_TitleAlignment,
						cafe["Title"]["Spacing"])
		return S

	def pdf_Annotate():
		#{{{
		S =""
		for n in range(len(Annotate)):
			Peak = Annotate[n]
			MZ = Peak[0]
			Label = Peak[1]
			Id = np.where( (DataX - MZ)**2 < 0.001)
			PeakHeight = max( DataY[ Id[0] ] )

			x = (MZ - xmin) * PS_ScalingFactor_X +\
					Origin[0] +\
					FontHeightRatio*AnnotateFontSize/2

			y = (PeakHeight - ymin) * PS_ScalingFactor_Y +\
					Origin[1] + AnnotateFontSize/2


			S += pdf.Print(	Label,
							x,
							y,
							#AnnotateWidth,
							20,
							AnnotateFont,
							AnnotateFontSize,
							pdf.ToPSColor(AnnotateFontColor),
							AnnotateAlignment,
							AnnotateSpacing,
							rotation = 90)
		return S#}}}

	def pdf_DrawAxis(Axis):
		#{{{
		AxesOrigin = [0,0]
		if isinstance(cafe["AxesOrigin"][0], str):
			AxesOrigin[0] = Origin[0]
		else:
			AxesOrigin[0] = xToPt(cafe["AxesOrigin"][0])

		if isinstance(cafe["AxesOrigin"][1], str):
			AxesOrigin[1] = Origin[1]
		else:
			AxesOrigin[1] = yToPt(cafe["AxesOrigin"][1])

		S=""
		if Axis ==1:
			#X axis
			S += pdf.DrawLines(
					[Origin[0],
						Origin[0] + Width],
					[AxesOrigin[1],
						AxesOrigin[1]],
					cafe["Xaxis"]["LineWidth"],
					"miter",
					pdf.ToPSColor(cafe["Xaxis"]["LineColor"]),
					pdf.ToPSDash(cafe["Xaxis"]["LineType"]))

		elif Axis ==2:
			#Y axis
			S += pdf.DrawLines(
					[Origin[0],
					Origin[0]],
					[Origin[1],
						Origin[1] + Height],
					cafe["Yaxis"]["LineWidth"],
					"miter",
					pdf.ToPSColor(cafe["Yaxis"]["LineColor"]),
					pdf.ToPSDash(cafe["Yaxis"]["LineType"]))

		if SecondaryAxis==True:
			S += pdf.DrawLines(
				[Origin[0]+Width,
				 Origin[0]+Width],
				[Origin[1],
				 Origin[1]+Height],
				cafe["AxesLineWidth"],
				"miter",
				[0,0,0],
				[[],0]
				)

		return S#}}}

	def pdf_PutErrorBar():
		if IsListOrArray(UpperError) and len(UpperError) == 0:
			return ""
		if IsListOrArray(LowerError) and len(LowerError) == 0:
			return ""
		#Check if Error contains list for multiplot
		if ThereIsListOrArrayWithinList( UpperError ):
			TheUpperError = UpperError[n]
			if not IsListOrArray(TheUpperError):
				TheUpperError = TheUpperError * np.ones(len(DataY))

		#if upper error and lower error are fixed value
		elif ( 	isinstance(UpperError,float) or
				isinstance(UpperError,int)
			):
			TheUpperError = UpperError * np.ones(len(DataY))
		else:
			print("[",n,"]"", ""Input Error for upper error bar !")
			return ""

		#Check if Error contains list for multiplot
		if ThereIsListOrArrayWithinList( LowerError ):
			TheLowerError = LowerError[n]
			if not IsListOrArray(TheLowerError):
				TheLowerError = TheLowerError * np.ones(len(DataY))

		#if upper error and lower error are fixed value
		elif ( 	isinstance(LowerError,float) or
				isinstance(LowerError,int)
			):
			TheLowerError = LowerError * np.ones(len(DataY))
		else:
			print("[",n,"]"", ""Input Error for Lower error bar !")
			return ""


		#Everthings look good :)
		UpperError_inPt = TheUpperError if cafe["LogY"] == False else\
					np.log10(TheUpperError)

		#Just in case it is a List
		UpperError_inPt = np.array(UpperError_inPt)
		UpperError_inPt =	UpperError_inPt * PS_ScalingFactor_Y

		LowerError_inPt = TheLowerError if cafe["LogY"] == False else\
						np.log10(TheLowerError)

		#Just in case it is a List
		LowerError_inPt = np.array(LowerError_inPt)

		LowerError_inPt = LowerError_inPt * PS_ScalingFactor_Y

		if cafe["Plot"]["ErrorBar"]["AutoLength"] == True:
			ErrorLength = cafe["Plot"]["ErrorBar"]["LengthOverWidth"] *Width
		else:
			ErrorLength = cafe["Plot"]["ErrorBar"]["Length"]

		return pdf.PutErrorBar(
					X_inPt,
					Y_inPt,
					UpperError_inPt,
					LowerError_inPt,
					ErrorLength,
					pdf.ToPSColor(Drink(cafe["Plot"]["ErrorBar"]["Color"],n)),
					Drink(cafe["Plot"]["ErrorBar"]["LineWidth"],n)
					)

	def killpdf_DrawAxes():
		#{{{
		AxesOrigin = [0,0]
		if isinstance(cafe["AxesOrigin"][0], str):
			AxesOrigin[0] = Origin[0]
		else:
			AxesOrigin[0] = xToPt(cafe["AxesOrigin"][0])

		if isinstance(cafe["AxesOrigin"][1], str):
			AxesOrigin[1] = Origin[1]
		else:
			AxesOrigin[1] = yToPt(cafe["AxesOrigin"][1])

		S=""
		S += pdf.DrawLines(
				[Origin[0],
					Origin[0] + Width],
				[AxesOrigin[1],
					AxesOrigin[1]],
				cafe["AxesLineWidth"],
				"miter",
				pdf.ToPSColor(cafe["AxesColor"]),
				[[],0])

		S += pdf.DrawLines(
				[AxesOrigin[0],
					AxesOrigin[0]],
				[Origin[1],
					Origin[1] + Height],
				cafe["AxesLineWidth"],
				"miter",
				pdf.ToPSColor(cafe["AxesColor"]),
				[[],0])

		if SecondaryAxis==True:
			S += pdf.DrawLines(
				[Origin[0]+Width,
				 Origin[0]+Width],
				[Origin[1],
				 Origin[1]+Height],
				cafe["AxesLineWidth"],
				"miter",
				[0,0,0],
				[[],0]
				)

		return S#}}}

	def pdf_DrawBarChart(X, Y,
			barwidth = 1, barlinewidth = 1,
			rgb=[0,0,0], fill = False, fillrgb = [0,0,0]):
		#{{{
		S = ""
		for n in range(len(X)):
			S += pdf.DrawBox(
						X[n] - barwidth/2,
						Origin[1],
						width	= barwidth,
						height	= Y[n]-Origin[1],
						linewidth	= barlinewidth,
						linergb		= rgb,
						dash		= [[],0],
						fillbox		= fill,
						fillrgb		= fillrgb
						)
		return S#}}}

	def xToPt(whatvalue):
		return (
				((whatvalue-xmin) if cafe["LogX"]== False else
					np.log10(whatvalue/xmin )
						)* PS_ScalingFactor_X + Origin[0]
				)

	def yToPt(whatvalue):
		return (
				((whatvalue-ymin) if cafe["LogY"]== False else
					np.log10(whatvalue/ymin )
						)* PS_ScalingFactor_Y + Origin[1]
				)

	def pdf_DrawEverythingExceptData():
		#{{{
		GS=""
		if cafe["Plot"]["PlotBox"]["Show"]:
			GS+= pdf.DrawBox(Origin[0],
							Origin[1],
							Width,
							Height,
							cafe["Plot"]["PlotBox"]["LineWidth"],
							pdf.ToPSColor(cafe["Plot"]["PlotBox"]["LineColor"]),
							pdf.ToPSDash(cafe["Plot"]["PlotBox"]["LineType"]),
							True,
							pdf.ToPSColor(cafe["Plot"]["PlotBox"]["BoxColor"])
							)
		#Label
		if len(cafe["xLabel"]["Text"]) != 0:
			GS += 	pdf_PutXlabel()
		if len(cafe["yLabel"]["Text"]) != 0:
			GS += 	pdf_PutYlabel()

		#Minor Tick
		if cafe["Xaxis"]["MinorTick"]["Show"] :
			GS += 	pdf_DrawMinorXtick()
		if cafe["Yaxis"]["MinorTick"]["Show"] :
			GS += 	pdf_DrawMinorYtick()

		#Tick
		if cafe["Xaxis"]["Tick"]["Show"] :
			GS += 	pdf_DrawXtick()
		if cafe["Yaxis"]["Tick"]["Show"] :
			GS += 	pdf_DrawYtick()

		#Minor Grid
		if cafe["Xaxis"]["MinorGrid"]["Show"] :
			GS += 	pdf_DrawMinorXgrid()
		if cafe["Yaxis"]["MinorGrid"]["Show"] :
			GS += 	pdf_DrawMinorYgrid()

		#Grid
		if cafe["Xaxis"]["Grid"]["Show"] :
			GS += 	pdf_DrawXgrid()
		if cafe["Yaxis"]["Grid"]["Show"] :
			GS += 	pdf_DrawYgrid()

		if len(cafe["Title"]) != 0:
			GS += 	pdf_PutTitle()
		if len(cafe["Annotate"]) !=0:
			GS +=	pdf_Annotate()

		#Axis Line
		if cafe["Xaxis"]["ShowAxis"] :
			GS += pdf_DrawAxis(1)
		if cafe["Yaxis"]["ShowAxis"] :
			GS += pdf_DrawAxis(2)

		return GS

	def UpdatePropertiesForAutoResizing():
		#{{{
		if cafe["Title"]["AutoFontSize"] == True:
			tfsoh = cafe["Title"]["FontSizeOverHeight"]
			cafe["Title"]["FontSize"]  = tfsoh * cafe["PlotRange"]["Height"]
			Print("TitleFontSize : " + str(cafe["Title"]["FontSize"]))

		global MinorTickLength
		if cafe["Xaxis"]["Tick"]["AutoLength"] == True:
			h = 1.0 * cafe["PlotRange"]["Height"]
			mtlotl = cafe["Xaxis"]["MinorTick"]["LengthOverTickLength"]
			tloh = cafe["Xaxis"]["Tick"]["LengthOverHeight"]
			MinorTickLength = h*mtlotl * tloh
		else:
			MinorTickLength =\
			 	cafe["Xaxis"]["MinorTick"]["LengthOverTickLength"] *\
				 cafe["Xaxis"]["Tick"]["Length"]

		if cafe["Yaxis"]["Tick"]["AutoLength"] == True:
			h = 1.0 * cafe["PlotRange"]["Height"]
			mtlotl = cafe["Yaxis"]["MinorTick"]["LengthOverTickLength"]
			tloh = cafe["Yaxis"]["Tick"]["LengthOverHeight"]
			MinorTickLength = h*mtlotl * tloh
		else:
			MinorTickLength =\
			 cafe["Yaxis"]["MinorTick"]["LengthOverTickLength"] *\
			  cafe["Yaxis"]["Tick"]["Length"]

		if cafe["Xaxis"]["Tick"]["AutoLength"]==True:
			tloh =  cafe["Xaxis"]["Tick"]["LengthOverHeight"]
			cafe["Xaxis"]["Tick"]["Length"] = tloh * cafe["PlotRange"]["Height"]

		if cafe["Yaxis"]["Tick"]["AutoLength"]==True:
			tloh =  cafe["Yaxis"]["Tick"]["LengthOverHeight"]
			cafe["Yaxis"]["Tick"]["Length"] = tloh * cafe["PlotRange"]["Height"]

		if cafe["Xaxis"]["Tick"]["AutoFontSize"] == True:
			tfsoh = cafe["Xaxis"]["Tick"]["FontSizeOverHeight"]
			cafe["Xaxis"]["Tick"]["FontSize"] = tfsoh * cafe["PlotRange"]["Height"]
			Print("xTickFontSize : " + str(cafe["Xaxis"]["Tick"]["FontSize"]) )

		if cafe["Yaxis"]["Tick"]["AutoFontSize"] == True:
			tfsoh = cafe["Yaxis"]["Tick"]["FontSizeOverHeight"]
			cafe["Yaxis"]["Tick"]["FontSize"] = tfsoh * cafe["PlotRange"]["Height"]
			Print("yTickFontSize : " + str(cafe["Yaxis"]["Tick"]["FontSize"]) )

		if cafe["xLabel"]["AutoFontSize"] == True:
			lfs = cafe["xLabel"]["FontSizeOverHeight"]
			cafe["xLabel"]["FontSize"] = lfs * cafe["PlotRange"]["Height"]
			Print("xLabelFontSize : " + str(cafe["xLabel"]["FontSize"]) )
		if cafe["yLabel"]["AutoFontSize"] == True:
			lfs = cafe["yLabel"]["FontSizeOverHeight"]
			cafe["yLabel"]["FontSize"] = lfs * cafe["PlotRange"]["Height"]
			Print("yLabelFontSize : " + str(cafe["yLabel"]["FontSize"]) )

		return#}}}
		#}}}End of Local Fucntion

	#{{{main codes in splot
	# Check if the data ara lists. If not, turn them into lists
	if (isinstance(DataYList, list) == False) &\
		(isinstance(DataXList, list) == False):
		DataXList = [DataXList]
		DataYList = [DataYList]

	# the following assumes all data are list arrays
	[plotxmin, plotxmax, plotymin, plotymax] = GetMinMaxForXYarray(
				DataXList, DataYList)

	if SecondaryAxis==True:
		cafe["Plot"]["LineColor"] = cafe["Plot2Color"]
		cafe["xlimit"]=cafe["x2limit"]
		cafe["ylimit"]=cafe["y2limit"]
	if len(cafe["Plot"]["xlimit"]) !=0:
		plotxmin = cafe["Plot"]["xlimit"][0]
		plotxmax = cafe["Plot"]["xlimit"][1]
	if len(cafe["Plot"]["ylimit"]) !=0:
		plotymin = cafe["Plot"]["ylimit"][0]
		plotymax = cafe["Plot"]["ylimit"][1]

	NumberOfPlot = len(DataYList)


	TitleWidth = cafe["Title"]["WidthRatio"]*Width

	UpdatePropertiesForAutoResizing()

	PrettyX= (mpretty([plotxmin, plotxmax],
						VerbalEcho= cafe["Debug"]["VerbalEchoForMpretty"])
			if cafe["LogX"]==False else logpretty([plotxmin, plotxmax],
						VerbalEcho= cafe["Debug"]["VerbalEchoForMpretty"])
			)
	PrettyY= (mpretty([plotymin, plotymax],
						VerbalEcho= cafe["Debug"]["VerbalEchoForMpretty"])
			if cafe["LogY"]==False else logpretty([plotymin, plotymax],
						VerbalEcho= cafe["Debug"]["VerbalEchoForMpretty"])
			)

	global xmin
	global ymin
	global PS_ScalingFactor_Y
	global PS_ScalingFactor_X


	xmin = PrettyX[0]
	xmax =  PrettyX[len(PrettyX)-1]
	ymin = PrettyY[0]
	ymax = PrettyY[len(PrettyY)-1]

	PlotYRange = (	(ymax - ymin) if cafe["LogY"]==False else
					np.log10(ymax/ymin)	)
	PlotXRange = (	(xmax - xmin) if cafe["LogX"]==False else
					np.log10(xmax/xmin)	)

	PS_ScalingFactor_Y = 1.0* Height / PlotYRange
	PS_ScalingFactor_X = 1.0* Width / PlotXRange

	XTickArray = PrettyX
	YTickArray = PrettyY

	XTickArray_inPt = xToPt(PrettyX)
	YTickArray_inPt = yToPt(PrettyY)
	MinorYTickArray = GenerateMinorTicks(
			YTickArray,
			TickNumber = cafe["Yaxis"]["MinorTick"]["TickNumber"],
			log = cafe["LogY"])

	MinorYTickArray_inPt = (
			np.log10(MinorYTickArray/ymin) if cafe["LogY"] else
			(MinorYTickArray - ymin)
							) *PS_ScalingFactor_Y + Origin[1]

	MinorXTickArray = GenerateMinorTicks(
			XTickArray,
			TickNumber = cafe["Xaxis"]["MinorTick"]["TickNumber"],
			log = cafe["LogX"])
	MinorXTickArray_inPt = (
			np.log10(MinorXTickArray/xmin) if cafe["LogX"] else
			(MinorXTickArray - xmin )
							) * PS_ScalingFactor_X + Origin[0]


	#Produce the important Graphic Stream
	GraphicsStream =""

	#Draw the frame, axes, tick etc
	if cafe["ShowDataOnly"]!=True:
		GraphicsStream += pdf_DrawEverythingExceptData()

	if PlotAxesOnly == True:
		#That 's all, good bye.
		return GraphicsStream

	for n in range(NumberOfPlot):
		DataX = DataXList[n]
		DataY = DataYList[n]

		# Just in case it is a List
		DataX = np.array(DataX)
		DataY = np.array(DataY)

		if len( cafe["Plot"]["xlimit"]) !=0:
			Index = np.where((DataX > cafe["Plot"]["xlimit"][0]) &
					(DataX < cafe["Plot"]["xlimit"][1]))
			DataX = DataX[Index[0]]
			DataY = DataY[Index[0]]

		X_inPt = (	(DataX-xmin) if cafe["LogX"] == False else
					np.log10(DataX/xmin)
					) * PS_ScalingFactor_X + Origin[0]

		Y_inPt = (	(DataY-ymin) if cafe["LogY"] == False else
					np.log10(DataY/ymin)
					) * PS_ScalingFactor_Y + Origin[1]

		if cafe["FillAreaUnderGraph"]:
			Xn = X_inPt[-1]
			X0 = X_inPt[0]
			Y0 = Y_inPt[0]
			if ymin > 0:
				Y00 = Origin[1]
			else:
				Y00 = (0 - ymin)*PS_ScalingFactor_Y + Origin[1]


			GraphicsStream += pdf.DrawClosedLine(
					np.append(X_inPt, [Xn, 	X0, 	X0]),
					np.append(Y_inPt, [ Y00, Y00, 	Y0]),
					linewidth = 0,
					linejoin = "round",
					pdf_RGB = [0,0,0],
					pdf_Dash=[[],0],
					fill = True,
					fillcolor = pdf.ToPSColor(
								Drink(cafe["FillAreaColor"],n)
								)
					)

		if Drink(cafe["Plot"]["LineType"], n) != "":
			GraphicsStream += 	pdf.DrawLines(
					X_inPt,
					Y_inPt,
					Drink(cafe["Plot"]["LineWidth"],n),
					"round",
					pdf.ToPSColor(Drink(cafe["Plot"]["LineColor"],n)),
					pdf.ToPSDash(Drink(cafe["Plot"]["LineType"],n))
					)

		if cafe["BarChart"]:
			GraphicsStream +=  pdf_DrawBarChart(X_inPt,
											Y_inPt,
											barwidth = 20,
											barlinewidth = 1,
											rgb=[0,0,0],
											fill = True,
											fillrgb = [0,0,0])



		if Drink(cafe["Plot"]["ErrorBar"]["Show"],n) == True:
			GraphicsStream += pdf_PutErrorBar()


		if cafe["Plot"]["Point"]["Show"] == True:
			if cafe["Plot"]["Point"]["AutoSize"]== True:
				pointsize = cafe["Plot"]["Point"]["SizeOverHeight"] *\
							cafe["PlotRange"]["Height"]
			else:
				pointsize = Drink(cafe["Plot"]["Point"]["Size"],n)
			Print("pointsize : " + str(pointsize))
			GraphicsStream += 	pdf.PutPoints (
								X_inPt, Y_inPt,
								Drink(cafe["Plot"]["Point"]["Type"],n),
								pointsize,
								pdf.ToPSColor(
									Drink(cafe["Plot"]["Point"]["Color"],n))
								)

	return GraphicsStream#}}}

# Plot one graph in one page
def plot(X, Y, sugar={}, coffee=myglobal.DEFAULT_PLOTSTYLE_FILENAME,
	X2=[], Y2=[], uppererror = [], lowererror=[]):

	#Check input format for X and Y
	if isinstance(X, np.ndarray):
		pass
	else:
		if isinstance(X, list):
			if isinstance(X[0], int) | isinstance(X[0], float):
				X = np.array(X)
			else:
				for x in X:
					if not isinstance(x,np.ndarray):
						x = np.array(x)
		else:
			print("Input Error")
			return -1
	if isinstance(Y, np.ndarray):
		pass
	else:
		if isinstance(Y, list):
			if isinstance(Y[0], int) | isinstance(Y[0], float):
				Y = np.array(Y)
			else:
				for y in Y:
					if not isinstance(y,np.ndarray):
						y = np.array(y)
		else:
			print("Input Error")
			return -1




	if load_cafe_as_global(coffee, sugar)==-1:
		return -1
	if cafe["PlotRange"]["AutoOrigin"] == True:
		cafe["PlotRange"]["Origin"][0] =\
		 	1.0*(cafe["Paper"]["Size"][0] - cafe["PlotRange"]["Width"])/2
		cafe["PlotRange"]["Origin"][1] =\
		 	1.0*(cafe["Paper"]["Size"][1] - cafe["PlotRange"]["Height"])/2
	S=""
	if cafe["Paper"]["Color"] !="":
		papersizestring  = GetPaperSize(cafe["Paper"]["Size"])
		paperwidth = int(papersizestring.split(" ")[0])
		paperheight = int(papersizestring.split(" ")[1])

		S+=	pdf.DrawBox(0,0,
				width=paperwidth,
				height=paperheight,
				linewidth=0,
				linergb=[0,0,0],
				dash=[[],0],
				fillbox=True,
				fillrgb = pdf.ToPSColor(cafe["Paper"]["Color"])
				)
	if cafe["Picture"]["InsertPicture"] == True:
		S += pdf.InsertPicture(
				cafe["Picture"]["PictureOrigin"],
				cafe["Picture"]["PictureSize"]
				)
	S += splot(X, Y,SecondaryAxis=False, UpperError=uppererror,LowerError=lowererror)
	if cafe["SecondaryAxis"]==True:
		S += splot(X2,Y2, SecondaryAxis=True,UpperError=uppererror,LowerError=lowererror)
	if S == -1:
		PrintError("Make no pdf")
		return -1
	else:
		pdf.makepdf(S,
			cafe["PDF"]["PDF_Compression"],
			cafe["Picture"]["InsertPicture"],
			cafe["Picture"]["PictureFilename"],
			cafe["PDF"]["UseJPEGForJPEGFile"],
			PaperSize=cafe["Paper"]["Size"],
			Unit=cafe["Paper"]["Unit"],
			PaperColor=cafe["Paper"]["Color"],
			ShowPDF=cafe["PDF"]["ShowPDF"],
			PDF_Viewer=cafe["PDF"]["PDF_Viewer"],
			PDF_Filename=cafe["PDF"]["PDF_Filename"])
	return 0



# Plot multiple graph in one page
def mplot(DataSet=[],
			sugar={},
			milk={},
			coffees = myglobal.DEFAULT_PLOTSTYLE_FILENAME,
			morecoffee = myglobal.DEFAULT_MULTI_PLOTSTYLE_FILENAME):
	if load_b_as_global(morecoffee, milk):
		return -1

	S=""
	if b["InsertPicture"] == True:
		S += pdf.InsertPicture(
				b["PictureOrigin"],
				b["PictureSize"]
				)

	if b["AutoOrigin"]:
		b["Origin"][0] = 1.0*(b["PaperSize"][0] - b["Width"])/2
		b["Origin"][1] = 1.0*(b["PaperSize"][1] - b["Height"])/2


	NumberOfMultiPlot = len(DataSet)
	if b["AutoAdjust"]:
		NumOfRow =  b["RowColumn"][0]
		NumOfColumn = b["RowColumn"][1]

		b["SubPlotWidth"] = 1.0*(b["Width"]-
								(NumOfColumn-1)*b["ColumnSpacing"]
								)/NumOfColumn
		b["SubPlotHeight"] = 1.0*(b["Height"]-
							(NumOfRow-1)*b["RowSpacing"]
							)/NumOfRow


		b["Origins"] = []
		for row in range(NumOfRow):
			for col in range(NumOfColumn):
				originx = b["Origin"][0] +\
							col*(
							b["ColumnSpacing"] +
							b["SubPlotWidth"])

				originy = b["Origin"][1] + b["Height"] -\
							b["SubPlotHeight"] -\
							row*(
							b["RowSpacing"] +
							b["SubPlotHeight"]
							)
				b["Origins"]+= [ [originx, originy] ]
	for n in range(NumberOfMultiPlot):
		coffee = Drink(coffees, n)

		if load_cafe_as_global(coffee, sugar)==-1:
			return -1

		cafe["Origin"] = b["Origins"][n]
		global Origin
		global Height
		global Width
		Origin = cafe["Origin"]
		Height = Drink(b["SubPlotHeight"],n)
		Width = Drink(b["SubPlotWidth"],n)

		S+= splot(	DataSet[n][0],
					DataSet[n][1],UpperError=uppererror,LowerError=lowererror)

	# Mutliplot settings overwrite
	# the settings for single plot
	cafe["Paper"]["Size"] = b["PaperSize"]
	pdf.makepdf(S, b["PDF_Compression"],
			b["InsertPicture"],
			b["PictureFilename"],
			b["UseJPEGForJPEGFile"],
			PaperSize=cafe["Paper"]["Size"],
			Unit=cafe["Paper"]["Unit"],
			PaperColor=cafe["Paper"]["Color"],
			ShowPDF=cafe["PDF"]["ShowPDF"],
			PDF_Viewer=cafe["PDF"]["PDF_Viewer"],
			PDF_Filename=cafe["PDF"]["PDF_Filename"])
	return

def polar(theta, radius, sugar={}, coffee=myglobal.DEFAULT_PLOTSTYLE_FILENAME):
	if load_cafe_as_global(coffee, sugar)== -1:
		return -1

	SecondaryAxis = False
	N = len(theta)
	if len(radius) != N:
		Print("Data Size error")
		return -1

	if isinstance (theta, list) == True:
		NumberOfDataSet = len(theta)
		x = [0] * NumberOfDataSet
		y = [0] * NumberOfDataSet

		for n in range(NumberOfDataSet):
			x[n] = abs(radius[n]) * np.cos(theta[n])
			y[n] = abs(radius[n]) * np.sin(theta[n])
	else:
		x = abs(radius) * np.cos(theta)
		y = abs(radius) * np.sin(theta)

	GraphicsStream = ""
	GraphicsStream += splot(x,y,SecondaryAxis)
	pdf.makepdf(GraphicsStream,
			cafe["PDF"]["PDF_Compression"],
			cafe["Picture"]["InsertPicture"],
			cafe["Picture"]["PictureFilename"],
			cafe["PDF"]["UseJPEGForJPEGFile"],
			PaperSize=cafe["Paper"]["Size"],
			Unit=cafe["Paper"]["Unit"],
			PaperColor=cafe["Paper"]["Color"],
			ShowPDF=cafe["PDF"]["ShowPDF"],
			PDF_Viewer=cafe["PDF"]["PDF_Viewer"],
			PDF_Filename=cafe["PDF"]["PDF_Filename"]
			)

def image(Mat = np.matrix([]), Xrange =[], Yrange=[],
		sugar={}, coffee=myglobal.DEFAULT_PLOTSTYLE_FILENAME):
	if load_cafe_as_global(coffee, sugar)== -1:
		return -1

	S =""
	if cafe["Picture"]["InsertPicture"] == True:
		S += pdf.InsertPicture(
					cafe["Picture"]["PictureOrigin"],
					cafe["Picture"]["PictureSize"]
					)

	cafe["Plot"]["PlotBox"]["Show"]=False
	#Set it false, or the PlotBox will Over

	S += pdf.InsertDataImage(
			cafe["PlotRange"]["Origin"],
			[cafe["PlotRange"]["Width"],cafe["PlotRange"]["Height"]]
			)

	if len(Mat) == 0:
		return -1
	if isinstance(Mat, np.matrix) == False:
		print ("Data should be in the form of numpy matrix")
		return -1

	cm = color.colormaps[ cafe["ColorMap"] ]
	Max = Mat.max()
	Min = Mat.min()
	Delta = Max -Min
	[Row,Col] = Mat.shape

	Data = [[0,0,0]]*(Col*Row)
	for c in range(Col):
		for r in range(Row):
			n = Col*r + c
			j = (Mat[r,c] - Min)/Delta * (len(cm) -1)
			j = int(round(j))
			Data[n] = [	cm[j][0]*128,
						cm[j][1]*128,
						cm[j][2]*128
						]
	#print(Data)
	if not isinstance(Xrange, np.ndarray):
		Xrange = np.array(Xrange)
	if not isinstance(Yrange, np.ndarray):
		Yrange = np.array(Yrange)

	S += splot(Xrange, Yrange, PlotAxesOnly=True)

	pdf.makepdf(S,
			cafe["PDF"]["PDF_Compression"],
			cafe["Picture"]["InsertPicture"],
			cafe["Picture"]["PictureFilename"],
			cafe["PDF"]["UseJPEGForJPEGFile"],
			Data,
			Col, Row,
			PaperSize=cafe["Paper"]["Size"],
			Unit=cafe["Paper"]["Unit"],
			PaperColor=cafe["Paper"]["Color"],
			ShowPDF=cafe["PDF"]["ShowPDF"],
			PDF_Viewer=cafe["PDF"]["PDF_Viewer"],
			PDF_Filename=cafe["PDF"]["PDF_Filename"])

def table(colnum = 4, rownum =4, prop ={}, propfile = myglobal.DEFAULT_PLOTSTYLE_FILENAME):
	try:
		global a
		JF=open(propfile,"r")
		cafe = json.loads(
				RemoveJsonComment(JF.read())
				)
	except Exception as e:
		PrintFatalError("Exception in loading json")
		print (e)
		JF.close() #redundent ?
		return -1
	finally:
		JF.close()


	origin = [100,100]
	TableHeight = 200
	TableWidth = 200
	height = TableHeight/rownum
	width = TableWidth/colnum
	S = ""
	S+= pdf.Draw_Rounded_Box(200,200, 100,100,40)
	makepdf(S)
	return

#{{{Acknowledment that shall be executed when imported
#	print ("-----------------------")
#	print ("Kopi 2017     <lcchen>")
#	print ("-----------------------")
#table()

#}}}
