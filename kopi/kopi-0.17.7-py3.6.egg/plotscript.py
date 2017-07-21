__all__ = ["splot"]

import numpy as np
from . import pdf
from .misc import *
from .mypretty import *
from .myfont import *

#The global dictionary here
#cafe = {}
FontHeightRatio = 0.7
SuperScript_FontSizeReduction = 4
Superscript_YoffsetRatio = 0.8
Subscript_FontSizeReduction = 4
Subscript_YoffsetRatio = 0.5
FontSizeEnlargementStep = 2
KeepFontSize = True

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
				[AxesOrigin[0],
					AxesOrigin[0]],
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

def splot(DataXList, DataYList,
		sweetcoffee,
		SecondAxis = False,
		PlotAxesOnly = False,
		):
	"""Main function to create the pdf graphic script.
	Return 0 if successful, and -1 is not."""

	global cafe
	cafe = sweetcoffee

	global Height
	Height = cafe["PlotRange"]["Height"]

	global Width
	Width = cafe["PlotRange"]["Width"]

	global Origin
	Origin = cafe["PlotRange"]["Origin"]

	global SecondaryAxis
	SecondaryAxis = SecondAxis

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

	global TitleWidth
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
	global YTickArray
	global XTickArray
	global MinorXTickArray_inPt
	global MinorYTickArray_inPt
	global XTickArray_inPt
	global YTickArray_inPt

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
								PlaySafe(cafe["FillAreaColor"],n)
								)
					)

		GraphicsStream += 	pdf.DrawLines(
				X_inPt,
				Y_inPt,
				PlaySafe(cafe["Plot"]["LineWidth"],n),
				"round",
				pdf.ToPSColor(PlaySafe(cafe["Plot"]["LineColor"],n)),
				pdf.ToPSDash(PlaySafe(cafe["Plot"]["LineType"],n))
				)

		if cafe["BarChart"]:
			GraphicsStream +=  pdf_DrawBarChart(X_inPt,
											Y_inPt,
											barwidth = 20,
											barlinewidth = 1,
											rgb=[0,0,0],
											fill = True,
											fillrgb = [0,0,0])

		if cafe["Plot"]["Point"]["Show"] == True:
			if cafe["Plot"]["Point"]["AutoSize"]== True:
				pointsize = cafe["Plot"]["Point"]["SizeOverHeight"] *\
				 			cafe["PlotRange"]["Height"]
			else:
				pointsize = PlaySafe(cafe["Plot"]["Point"]["Size"],n)
			Print("pointsize : " + str(pointsize))
			GraphicsStream += 	pdf.PutPoints (
								X_inPt, Y_inPt,
								PlaySafe(cafe["Plot"]["Point"]["Type"],n),
								pointsize,
								pdf.ToPSColor(
									PlaySafe(cafe["Plot"]["Point"]["Color"],n))
								)

	return GraphicsStream#}}}
