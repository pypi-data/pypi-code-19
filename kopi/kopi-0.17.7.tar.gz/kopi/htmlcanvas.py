"""
	Collection of small modules to handle html canvas script.

	Similar to pdf.py, the subroutine here are used to produced near
	equivalent appreance in webbrowser as that in pdf reader counter part.

"""
import numpy as np
from datetime import datetime
import os
import zlib as gzip
from .misc import *
from .myfont import GetStringWidth, ShortFontName
from .myimage import *
from .mycolor import *
#from .font import ShortFontName
# Global Variable for Making  PDF
CurrentRGB_Stroking= [0,0,0]
CurrentRGB_NonStroking= [0,0,0]
CurrentLineWidth= 0
CurrentDash = [[],0]
CurrentRotateAngle = 0
CurrentLineJoin= "miter"
CurrentFont= ""
CurrentFontSize= 0


CanvasContext = "ctx"
CanvasContextDot = CanvasContext + "."
JavaEOL ="\n" #May not be necessary
global PaperHeight
def ToCanvasY(y):
	#The coordinates for Canvas and PDF are different
	# Canvas:	|------>
	#			|
	#			+
	#
	# pdf:		^
	#			|
	#
	if 'numpy' in str(type(y)):
		y = 1.0*PaperHeight - 1.0* y
		return y
	if isinstance(y, list):
		for yelement in y:
			yelement =  1.0*PaperHeight - 1.0* yelement
		return y
	y = 1.0*PaperHeight - 1.0* y
	return y

def ToRelativeCanvasY(y):
	# To de-translate back to the origin
	# pdf:		^
	#			|
	#			|		#
	#			|		|
	#			|>	>	|
	#			O	_	_	_>
	#Canvas
	#			O	_	_	_>
	#			|		|
	#			|		#
	#			|
	#			|
	#			|
	if 'numpy' in str(type(y)):
		y =  -1.0*PaperHeight - 1.0* y
		return y
	if isinstance(y, list):
		for yelement in y:
			yelement = -1.0*PaperHeight - 1.0* yelement
		return y
	y= -1.0*PaperHeight - 1.0* y
	return y

def RGBtoPostScriptRGB(StandardRGB = [255, 255, 255]):#{{{
	# PostScript or PDF takes rgb value from 0 to 1.0 instead of 0 to 255
	PostScriptRGB = np.array([1.0, 1.0, 1.0])
	PostScriptRGB[0] = 1.0*StandardRGB[0]/255
	PostScriptRGB[1] = 1.0*StandardRGB[1]/255
	PostScriptRGB[2] = 1.0*StandardRGB[2]/255
	return PostScriptRGB#}}}

def ToPSColor(Color="black"):
	#If Verbal color contain something, then use that as color
	if Color == "":
		return "#FFFFFF"

	if Color[0]=="#":
		return Color


	Standard_RGB =  ColorNameToRGB(Color)
	R = ("%2x"%Standard_RGB[0]).replace(" ","0")
	G = ("%2x"%Standard_RGB[1]).replace(" ","0")
	B = ("%2x"%Standard_RGB[2]).replace(" ","0")
	return "#" + R + G + B

def ToPSDash(Dash="-"):#{{{
	if Dash == "-":
		return [[],0]
	if Dash == "--":
		# dash 4 mm, space 2 mm following US CAD standard
		DashLength = mm_to_pt(4)
		SpaceLength = mm_to_pt(2)
		return [[DashLength, SpaceLength],0]
	if Dash ==".":
		# dash 1 mm, space 1 mm
		return [[	mm_to_pt(1),
					mm_to_pt(1)],	0]
	if Dash == "-.-":
		return [[	mm_to_pt(5),
					mm_to_pt(3),
					mm_to_pt(1),
					mm_to_pt(3)], 0]
	if isinstance(Dash, list):
		#Correct format for manual assignment:
		#[[10,20],0]
		if isinstance(Dash[0],list) &\
			isinstance(Dash[1], int):
			return Dash
	return [[],0]#}}}

global Translated
Translated=False
def translate(tx, ty):
	global Translated
	#ctx.translate(70,70)
	if Translated:
		#use relative coordinate
		ty = ToRelativeCanvasY(ty)
		Translated = False
	else:
		#used absolute coordinate
		ty = ToCanvasY(ty)
		Translated = True
	return CanvasContextDot +\
			"translate(" +\
	 		str(tx) + "," + str(ty) + ");" + JavaEOL

def lineto(x, y):
	#ctx.lineTo(200,100);
	y = ToCanvasY(y)
	return CanvasContextDot +\
			"lineTo(" +\
			ftos(x) + "," + ftos(y) + ");" + JavaEOL
def beginPath():
	#ctx.beginPath();
	return CanvasContextDot +\
			"beginPath();" + JavaEOL

def moveto(x, y):
	#ctx.moveTo(0,0);
	y = ToCanvasY(y)
	return beginPath()+\
			CanvasContextDot +\
			"moveTo(" +\
			ftos(x) + "," + ftos(y) + ");" + JavaEOL
def scale (x,y):
	#ctx.scale(2,2);
	return CanvasContextDot +\
			"scale(" +\
			ftos(x) + "," + ftos(y) + ");" + JavaEOL

def stroke():
	#ctx.stroke();
	return CanvasContextDot +\
			"stroke();" + JavaEOL

def close():
	#ctx.closePath();
	return CanvasContextDot +\
			"closePath();" + JavaEOL

def close_stroke():
	return close() + stroke()

def fill():
	#context.fill();
	return CanvasContextDot +\
	 		"fill();" + JavaEOL

def close_fill_only():
	return close() + fill()

def fill_stroke():
	return fill() + stroke()

def close_fill_stroke():
	return close() + fill() + stroke()

def close_shade():
	return "W n q \n" + "/S1 sh Q\n"
	#return "h /S1 sh\n"

def set_pattern():
	return "/Pattern cs\n"+\
			"/P1 scn\n"

def rectangle(x,y,width, height):
	#ctx.rect(20,20,150,100);
	#y = ToCanvasY(y)
	y = PaperHeight - height - y
	return CanvasContextDot +\
			"rect(" +\
			ftos(x) +"," + ftos(y) + "," +\
			ftos(width) + "," + ftos(height) +\
			 ");" + JavaEOL

def curveto(x1, y1, x2, y2, x3, y3):
	#ctx.bezierCurveTo(20,100,200,100,200,20);
	y1 = ToCanvasY(y1)
	y2 = ToCanvasY(y2)
	y3 = ToCanvasY(y3)

	return CanvasContextDot +\
			"bezierCurveTo(" +\
			ftos(x1) + "," + ftos(y1) + "," +\
			ftos(x2) + "," + ftos(y2) + "," +\
			ftos(x3) + "," +ftos(y3) + ");" + JavaEOL

def setlinewidth(linewidth):
	global CurrentLineWidth
	if linewidth == CurrentLineWidth:
		return ""
	CurrentLineWidth = linewidth
	#ctx.lineWidth=10
	return CanvasContextDot +\
			"lineWidth=" +\
			ftos(linewidth) + ";"+ JavaEOL

def setdash(pdf_DashArray, pdf_DashOffset):
	global CurrentDash
	if (pdf_DashArray == CurrentDash[0] ) and\
	(pdf_DashOffset) == CurrentDash[1]:
		return ""
	CurrentDash[0] = pdf_DashArray
	CurrentDash[1] = pdf_DashOffset
	#ctx.setLineDash([5, 15])
	List=""
	for n in range(len (pdf_DashArray)):
		List += ftos(pdf_DashArray[n])
		if n < (len(pdf_DashArray) -1):
			List += ","
	return CanvasContextDot +\
			"setLineDash([" +\
	 		List + "]);" + JavaEOL

def setlinejoin(JoinType="miter"):
	global CurrentLineJoin
	if JoinType == CurrentLineJoin:
		return ""
	CurrentLineJoin = JoinType
	#ctx.lineJoin="round";
	S = ""
	if JoinType == "miter":
		S += "0"
	elif JoinType == "round":
		S += "1"
	elif JoinType == "bevel":
		S += "2"
	else:
		S += "0"
	return CanvasContextDot +\
			"lineJoin=" + "\""+\
			JoinType + "\";" + JavaEOL

def setrgb_stroking(color):
	global CurrentRGB_Stroking
	if color == CurrentRGB_Stroking:
		return ""
	CurrentRGB_Stroking = color
	#ctx.fillStyle = 'green';
	return CanvasContextDot +\
			"strokeStyle =\'" + color + "\';" + JavaEOL

def setrgb_nonstroking(color):
	global CurrentRGB_NonStroking
	if color == CurrentRGB_NonStroking:
		return ""
	CurrentRGB_NonStroking = color
	#ctx.fillStyle = 'green';
	return CanvasContextDot +\
			"fillStyle =\'" + color + "\';" + JavaEOL

def killsetrgb_nonstroking(pdf_rgb):
	global CurrentRGB_NonStroking

	if isinstance (pdf_rgb, str):
	#Testhere
		S =""
		S += set_pattern()
		return S

	if (pdf_rgb[0] == CurrentRGB_NonStroking[0]) & \
			(pdf_rgb[1] == CurrentRGB_NonStroking[1]) & \
			(pdf_rgb[2] == CurrentRGB_NonStroking[2]):
		return ""
	else:
		CurrentRGB_NonStroking[0] = pdf_rgb[0]
		CurrentRGB_NonStroking[1] = pdf_rgb[1]
		CurrentRGB_NonStroking[2] = pdf_rgb[2]
		return (ftos(pdf_rgb[0]) + " " +\
						ftos(pdf_rgb[1]) + " " +\
						ftos(pdf_rgb[2]) + " rg\n")

def Initialize(paperheight):
	global PaperHeight
	PaperHeight = paperheight

	return

def Draw_Rounded_Box(x, y,width, height, radius,
		linewidth=0.0, linecolor= "black", dash = [[],0],
		fillbox = True, fillcolor="yellow"):
    # Quater number count clockwisely from upper right.
	hw = 0.5*width	#half width
	hh = 0.5*height	#half height
	S=""

	# take some precausion so the
	# the radius for the rounded corner is smaller
	# than the dimension
	if height < width:
		MinDimension = height
	else:
		MinDimension = width
	if radius > MinDimension:
		radius = MinDimension

	S += moveto(	x,
						y + hh)

	S += lineto(	x + hw - radius,
						y + hh)

	S += quartercircle(
						x + hw - radius,
						y + hh - radius,
						radius,
						quarter = 1)

	S += lineto(	x + hw,
						y - hh + radius)

	S += quartercircle(
						x + hw - radius,
						y - hh + radius,
						radius,
						quarter = 2)

	S += lineto(	x - hw + radius,
						y - hh)

	S += quartercircle(
						x - hw + radius,
						y - hh + radius,
						radius,
						quarter = 3)

	S += lineto(	x - hw,
						y + hh - radius)

	S += quartercircle(
						x - hw + radius,
						y + hh - radius,
						radius,
						quarter = 4)

	S += setlinewidth(linewidth) +\
			setdash(dash[0], dash[1]) +\
			setrgb_stroking(ToPSColor(linecolor))

	if fillbox == True:
		S += setrgb_nonstroking(ToPSColor(fillcolor))
		if linewidth == 0:
			S += fill()
		else:
			S += close_fill_stroke()
	else:
		S += close_stroke()
	return S

def quartercircle(x, y,radius, quarter=1):

	# x and y are the next point

	# Reference: 2011 by Spencer Mortensen.
	# http://spencermortensen.com/articles/bezier-circle/
	#A good cubic Bezier approximation to a circular arc is:
	#P_0 = (0,1), P_1 = (c,1), P_2 = (1,c), P_3 = (1,0)
	#c = 0.551915024494
	#This yields an arc on the unit circle centered about the origin,
	#starting at P_0 and and ending at P_3, with the least amount of radial drift.

	S = ""
	magic = 0.551915024494
	if quarter == 1:
		S += curveto(
					x + magic*radius,
					y + radius,
					x + radius,
					y + magic*radius,
					x + radius,
					y + 0)

	elif quarter == 2:
		S += curveto(
					x + radius,
					y - 1.0*magic*radius,
					x + magic*radius,
					y - 1.0*radius,
					x + 0,
					y - 1*radius)

	elif quarter == 3:
		S += curveto(
					x - 1.0*magic*radius,
					y - 1*radius,
					x - 1.0*radius,
					y - 1*magic*radius,
					x - 1*radius,
					y + 0)

	elif quarter == 4:
		S += curveto(
					x - 1*radius,
					y + magic*radius,
					x - 1*magic*radius,
					y + radius,
					x + 0,
					y + radius)
	else:
		raise Exception("parameters to draw quarter circle not valid")
	return S

def circle_path_only(x, y, radius):

	magic = 0.551915024494
	S = ""
	S = moveto(	x, y + radius )

	S += curveto(
				x + magic*radius,
				y + radius,
				x + radius,
				y + magic*radius,
				x + radius,
				y + 0)

	S += curveto(
				x + radius,
				y - 1.0*magic*radius,
				x + magic*radius,
				y - 1.0*radius,
				x + 0,
				y - 1*radius)

	S += curveto(
				x - 1.0*magic*radius,
				y - 1*radius,
				x - 1.0*radius,
				y - 1*magic*radius,
				x - 1*radius,
				y + 0)

	S += curveto(
				x - 1*radius,
				y + magic*radius,
				x - 1*magic*radius,
				y + radius,
				x + 0,
				y + radius)
	return S

def circle_stroke_only(x, y, radius, linewidth, rgb, dash):

	S = circle_path_only(x, y, radius)
	S += (	setdash(dash[0], dash[1]) +
		setrgb_stroking(rgb) + setlinewidth(linewidth) )

	S += stroke()
	return S

def circle_fill_only(x, y, radius, rgb):

	S = circle_path_only(x, y, radius)
	S += setrgb_nonstroking(rgb)
	S += fill()
	return S

def circle_fill_stroke(x, y, radius, linewidth, linergb,
		dash,fillrgb ):
	S = circle_path_only(x, y, radius)
	S += (	setdash(dash[0], dash[1]) +
		setrgb_stroking(linergb) +
		setlinewidth(linewidth) +
		setrgb_nonstroking(fillrgb))

	S += fill_stroke()
	return S

def selectfont(font, fontsize):
	#ctx.font = "30px Arial";
	f = ShortFontName[font]
	return CanvasContextDot +\
			"font=\"" +\
			ftos(fontsize) + "pt " +\
			font + "\"" + JavaEOL

def setrotate(angle_degree):
	#ctx.rotate(45 * Math.PI / 180);
	#radian = np.pi*1.0*angle_degree/180
	return	CanvasContextDot +\
			"rotate(" + str(-angle_degree) +\
			"* Math.PI/180);" + JavaEOL

def gsave():
	return "q\n"

def grestore():
	return "Q\n"

def KillDrawLine(x1, y1, x2, y2,
		linewidth=1, pdf_rgb=[0,0,0], pdf_dash=[[],0]):
	y1 = ToCanvasY(y1)
	y2 = ToCanvasY(y2)
	S=""
	S+= (	setlinewidth(linewidth) +
		setdash(pdf_dash[0], pdf_dash[1]) +
		setrgb_stroking(pdf_rgb))
	S+= (moveto(x1,y1) + lineto(x2, y2))
	S+= stroke()
	return S

def DrawLines(xa, ya, linewidth, linejoin, pdf_RGB, pdf_Dash):
	#ya = ToCanvasY(ya)
	#y2 = ToCanvasY(y2)
	#print ("here?............?")
	if len(xa) > 1:
		OutputString =""
		OutputString += (
				setdash(pdf_Dash[0], pdf_Dash[1]) +
				setrgb_stroking(pdf_RGB) +
				setlinewidth(linewidth)
				)
		if linejoin == "miter":
			OutputString+= setlinejoin("miter")
		elif linejoin == "round":
			OutputString +=  setlinejoin("round")
		elif linejoin == "bevel":
			OutputString +=  setlinejoin("bevel")

		OutputString +=  moveto( xa[0], ya[0])
		for n in range(len(xa)-1):
			OutputString += lineto(xa[n+1], ya[n+1])

		OutputString += stroke()
		return OutputString
	else:
		print ("Need 2 or more points to draw line--> DO Nothing\n")
		return ""

def DrawClosedLine(xa, ya, linewidth,
		linejoin, pdf_RGB, pdf_Dash,
		fill=False, fillcolor=[0,0,0]):
	#For filled polar plot or plot with filled Area under graph
	#Essentially the same as DrawLines, but terminated with
	#close_stroke
	if len(xa) < 2:
		print ("Need 2 or more points to draw line--> DO Nothing\n")
		return ""

	OutputString =""
	OutputString +=\
			setdash(pdf_Dash[0], pdf_Dash[1]) +\
			setrgb_stroking(pdf_RGB) +\
			setlinewidth(linewidth) +\
			setrgb_nonstroking(fillcolor)


	if linejoin == "miter":
		OutputString+= setlinejoin("miter")
	elif linejoin == "round":
		OutputString +=  setlinejoin("round")
	elif linejoin == "bevel":
		OutputString +=  setlinejoin("bevel")

	OutputString +=  moveto( xa[0], ya[0])
	for n in range(len(xa)-1):
		OutputString += lineto(xa[n+1], ya[n+1])

	if fill == False:
		OutputString += close_stroke()
	else:
		if linewidth == 0:
			OutputString += close_fill_only()
		else:
			OutputString += close_fill_stroke()

	return OutputString

def DrawBox(x,y,width,height,
		linewidth, linergb, dash, fillbox, fillrgb):

	S =""
	S += rectangle(x,y,width,height)

	if linewidth == 0:
		if fillbox==True:
			S += setrgb_nonstroking(fillrgb)
			S += fill()
		else:
			print ("Warning: No fill, No stroke. What do you want ?\n")
	else:
		if (fillbox==True):
			S += setrgb_nonstroking(fillrgb)
			S += (setlinewidth(linewidth) + setdash(dash[0], dash[1]) + setrgb_stroking(linergb) )
			S += fill_stroke()

		else:
			S += (setlinewidth(linewidth) + setdash(dash[0], dash[1]) + setrgb_stroking(linergb) )
			S += stroke()
	return S

def DrawCross(x, y, height, kind="times", linewidth=1, rgb=[0,0,0]):

	S =""
	S += setlinewidth(linewidth)
	S += setrgb_stroking(rgb)

	if kind == "multiply_long":
		S += moveto(x-0.5*height , y - 0.5* height)
		S += lineto(x+0.5*height, y + 0.5*height)
		S += moveto(x - 0.5*height, y+0.5*height)
		S += lineto(x + 0.5*height, y-0.5*height)
	elif kind == "multiply":
		d = 0.5*height/np.sqrt(2) #0.5*h*cos(45degree)
		S += moveto(x- d , y - d)
		S += lineto(x + d, y + d )
		S += moveto(x - d, y + d )
		S += lineto(x + d , y - d)

	elif kind == "plus":
		S += moveto(x , y + 0.5* height)
		S += lineto(x, y - 0.5*height)
		S += moveto(x - 0.5*height, y)
		S += lineto(x + 0.5*height, y)
	S += stroke()
	return S

def triangle_path_only(center_x, center_y, height, direction="up"):

	L = 2.0 * height / np.sqrt(3)
	a = height/3
	b = height -a
	if direction=="up":
		S = moveto(center_x - 0.5*L  , center_y - a)
		S += lineto(center_x , center_y + b)
		S += lineto(center_x + 0.5*L , center_y - a)

	elif direction == "down":
		S = moveto(center_x - 0.5*L  , center_y + a)
		S += lineto(center_x , center_y - b)
		S += lineto(center_x + 0.5*L , center_y + a)

	elif direction == "left":
		S = moveto(center_x + a  , center_y -L/2)
		S += lineto(center_x - b , center_y )
		S += lineto(center_x + a, center_y + L/2)

	elif direction == "right":
		S = moveto(center_x - a  , center_y -L/2)
		S += lineto(center_x + b , center_y )
		S += lineto(center_x - a, center_y + L/2)

	S += close()
	return S

def triangle_stroke_only(x, y, height, direction, linewidth, rgb):

	S = triangle_path_only(x, y, height, direction)
	S += (setrgb_stroking(rgb) +
		setlinewidth(linewidth))
	S += stroke()
	return S

def triangle_fill_only(x, y, height, direction, rgb):

	S = triangle_path_only(x, y, height, direction)
	S += setrgb_nonstroking(rgb)
	S += fill()
	return S

def PutPoints (xa, ya, point, height, rgb, linewidth=1):

	S = ""
	if point[0] =="\\":
			pointtext=point[1:len(point)]
			S += 	PutTextArray(xa, ya, [pointtext]*len(xa),
				fontname.Helvetica, height, rgb, 0, [0.5,0.4] )
	else:
		for n in range(len(xa)):
			if point == "SolidCircle":
				S += circle_fill_only(xa[n], ya[n], 0.5* height, rgb)
			elif point == "OpenCircle":
				S += circle_stroke_only(xa[n], ya[n], 0.5* height,
					linewidth, rgb, [[],0])
			elif point == "SolidSquare" :
				S += DrawBox(xa[n] - 0.5* height,
						ya[n] - 0.5* height,
						 height,  height, 0, [0,0,0], [[],0], True, rgb)
			elif point == "OpenSquare" :
				S += DrawBox(xa[n] - 0.5* height,
						ya[n] - 0.5* height,
						 height,  height, linewidth,
						 rgb, [[],0], False, [0,0,0])
			elif point == "SolidTriangle" :
				S += triangle_fill_only(xa[n], ya[n],
									height, "up", rgb)

			elif point == "OpenTriangle" :
				S += triangle_stroke_only(xa[n], ya[n],
							height, "up", linewidth, rgb)

			elif point == "OpenTriangle" :
				S += triangle_stroke_only(xa[n],
							ya[n], height, "down", linewidth, rgb)

			elif point == "OpenDownwardTriangle":
				S += triangle_stroke_only(xa[n], ya[n],
							height, "down", linewidth, rgb)

			elif point == "SolidDownwardTriangle":
				S += triangle_fill_only(xa[n], ya[n],
							height, "down", rgb)

			elif point == "SolidLeftwardTriangle":
				S += triangle_fill_only(xa[n], ya[n],
							height, "left", rgb)

			elif point == "SolidRightwardTriangle":
				S += triangle_fill_only(xa[n], ya[n],
							height, "right", rgb)

			elif point == "OpenLeftwardTriangle":
				S += triangle_stroke_only(xa[n], ya[n],
							height, "down", linewidth, rgb)

			elif point == "OpenRightwardTriangle":
				S += triangle_stroke_only(xa[n], ya[n],
							height, "right", linewidth, rgb)

			elif point == "DoubleTriangle":
				S += triangle_stroke_only(xa[n], ya[n],
							height, "up", linewidth, rgb)
				S += triangle_stroke_only(xa[n], ya[n],
							height, "down", linewidth, rgb)

			elif point == "Cross"	:
				S += DrawCross(xa[n], ya[n],
							height, "multiply", linewidth, rgb)

			elif point == "Plus"	:
				S += DrawCross(xa[n], ya[n],
							height, "plus", linewidth, rgb)

			elif point == "CrossPlus":
				S += DrawCross(xa[n], ya[n],
							height, "plus", linewidth, rgb)
				S += DrawCross(xa[n], ya[n],
							height, "multiply", linewidth, rgb)

			elif point == "BoxPlus":
				S += DrawBox(xa[n] - 0.5* height,ya[n] - 0.5* height,
						 height,  height, linewidth, rgb, [[],0], False, [0,0,0])
				S += DrawCross(xa[n], ya[n], height, "plus", linewidth, rgb)

			elif point == "BoxCross":
				S += DrawBox(xa[n] - 0.5* height,ya[n] - 0.5* height,
						 height,  height, linewidth, rgb, [[],0], False, [0,0,0])
				S += DrawCross(xa[n], ya[n], height, "multiply_long", linewidth, rgb)
			else:
				S += circle_fill_only(xa[n], ya[n], 0.5* height, rgb)
	return S

def PutText(x, y, text, font, fontsize, rgb, rotation, alignment):
	#	Defination for Alignment:
	#	 XXx
	#	^	this is the default [0,0,], Bottom-Left Aligned
	#	 XXx
	#	  ^	this is [0.5, 0]  Bottom-Center Aligned
	#	 XXx
	#	   ^	this is [1,0] 	Right-Aligned
	#	Same rules applied to Vertical Axis.
	#	eg:
	#	_
	#	 XXx	this is [0,1] Upper-Left Aligned
	#	   _
	#	 XXx	this is [1,1) Upper-Roght Aligned.
	#
	#	However, FontSize and the actual font height are not exactly equal,
	#	so, some fine tuning needs to be done to give perfect alignemnt effect.
	#ctx.font = "30px Arial";
	#y = ToCanvasY(y)

	stringwidth=GetStringWidth(text, font, fontsize)
	#text=InsertEscapeBeforeParenthesis(text)
	S=""
	S +=  translate(x, y)

	if rotation !=0:
		S += setrotate(rotation)

	#S += "BT\n"
	S += (	setrgb_nonstroking(rgb) +
		selectfont(font, fontsize) )

	#S += text_position(0, 0)
	xo = 0
	yo = 0

	if (alignment[0]!= 0) | (alignment[1] !=0 ):
		xoffset = -1.0 * alignment[0] * stringwidth
		yoffset = -1.0 * alignment[1] * fontsize
		#S += text_position(xoffset, yoffset)
		xo = 1.4*xoffset
		yo = -1.3*yoffset

	#ctx.fillText("Hello World",10,50);
	S += CanvasContextDot +\
		"fillText(\"" +\
		text + "\"," + str(xo)+","+str(yo) +");" + JavaEOL
	#S += show_text(text)
	#S += "ET\n"

	if rotation !=0:
		S += setrotate(-rotation)

	S += translate(-x, -y)

	return S

def DrawLine_WithoutChangingLinewidthDashColor(X1, Y1, X2,Y2):
	return (moveto(X1,Y1)+ lineto(X2,Y2)+ stroke())

def DrawXTick(origin, xtickvector,
		tickheight,	#default:
					#Tick out(positive value,
					#rather then ticking in as in R and Python.
		ticklinewidth,
		tickrgb,
		tickdash=[[],0]
		):

	S =""
	S +=  ( setrgb_stroking(tickrgb) + setlinewidth( ticklinewidth) + setdash(tickdash[0], tickdash[1]))

	for n in range(len( xtickvector)):
		S += DrawLine_WithoutChangingLinewidthDashColor(
				xtickvector[n], origin[1],
				xtickvector[n], origin[1] - tickheight
				)
	return S

def DrawYTick(origin, yticks,
		tickheight, ticklinewidth, rgb,tickdash=[[],0]):

	S=""
	S +=  (setrgb_stroking(rgb) + setlinewidth(ticklinewidth) + setdash(tickdash[0],tickdash[1]))
	for n in range( len(yticks)):
		S += DrawLine_WithoutChangingLinewidthDashColor(
				origin[0], yticks[n],
				origin[0]- tickheight, yticks[n])
	return S

def PutTextArray(x_vector, y_vector,
		textarray, font, fontSize, rgb, rotation, alignment):
	S =""
	if (len(x_vector)-len(textarray)) ==0:
		for n in range( len( textarray ) ):
			S += PutText(x_vector[n],
						y_vector[n],
						textarray[n],
						font,
						fontSize,
						rgb,
						rotation,
						alignment)
	else:
		print ("Error\n")
		S=""
	return S

def Print(string, x, y, xwidth,
		font, fontsize, rgb, xalignment, linespacing, rotation = 0):

	#rotation=0
	S = ""
	S += setrgb_nonstroking(rgb)
	[SegmentContent, SegmentAttri] = BreakStringIntoSegments( string )
	CursorPosition = 0
	Cursor_Yoffset = 0

	for k in range(len(SegmentContent)):
		if (SegmentAttri[k] == "Italic") | (SegmentAttri[k] == "Bold"):
			TobeRestoredFont = font
			font = ChangeFontAttrib(font, SegmentAttri[k])
		elif (SegmentAttri[k] == "superscript") | (SegmentAttri[k] == "subscript"):
			TobeRestored_fontsize = fontsize
			[fontsize, Cursor_Yoffset] = ChangeSuperSub(fontsize, SegmentAttri[k])
		elif (SegmentAttri[k] == "Large") |\
				(SegmentAttri[k] == "large")|\
				(SegmentAttri[k] == "Small") |\
				(SegmentAttri[k] == "small"):
			TobeRestored_fontsize = fontsize
			fontsize = ChangeFontSize(fontsize, SegmentAttri[k])

		elif (SegmentAttri[k][0:5] == "color"):
			newcolor =  SegmentAttri[k][6: len(SegmentAttri[k]) ]
			RestoredRGB = rgb
			rgb = ToPSColor(newcolor)

		elif (SegmentAttri[k][0:5] == "font:"):
			newfont =  SegmentAttri[k][5: len(SegmentAttri[k]) ]
			RestoredFont = font
			font = newfont

		elif (SegmentAttri[k][0:6] == "rotate"):
			rotation =  float(SegmentAttri[k][7: len(SegmentAttri[k]) ] )

		S += PutText(
				x + CursorPosition,
				y + Cursor_Yoffset,
				SegmentContent[k],
				font,
				fontsize,
				rgb,
				rotation,
				[xalignment,0],
				)
		CursorPosition += GetStringWidth(SegmentContent[k], font, fontsize)

		if (SegmentAttri[k] == "Italic") | (SegmentAttri[k] == "Bold"):
			font=TobeRestoredFont

		elif (SegmentAttri[k] == "superscript") |\
				(SegmentAttri[k] == "subscript") |\
				(SegmentAttri[k] == "Large") |\
				(SegmentAttri[k] == "large")|\
				(SegmentAttri[k] == "Small") |\
				(SegmentAttri[k] == "small"):
			fontsize = TobeRestored_fontsize
			Cursor_Yoffset=0
		elif (SegmentAttri[k][0:5] == "color"):
			rgb = RestoredRGB
		elif (SegmentAttri[k][0:5] == "font:"):
			font = RestoredFont
		elif (SegmentAttri[k][0:6] == "rotate"):
			rotation = 0

	#dummy to rest pdf setting
	S += PutText(
		x + CursorPosition,
		y + Cursor_Yoffset,
		"",
		font,
		fontsize,
		rgb,
		rotation,
		[xalignment,0],
		)
	return S

def InsertDataImage(imageorigin, imagesize):
	w = imagesize[0]
	h = imagesize[1]
	x = imageorigin[0]
	y = imageorigin[1]
	S	= "q\n" +\
		str(w) + " 0 0 " +\
		str(h) + " " +\
		str(x) + " " +\
		str(y) + " cm\n" +\
		"/DataImg0 Do\n"+\
		"Q\n"
	return S
def InsertPicture(pictureorigin, picturesize ):#x, y, w, h):

	#Eg: "400 0 0 400 200 150 cm\n"

	if isinstance(pictureorigin[0], list) == False:
		w = picturesize[0]
		h = picturesize[1]
		x = pictureorigin[0]
		y = pictureorigin[1]
		S	= "q\n" +\
			str(w) + " 0 0 " +\
			str(h) + " " +\
			str(x) + " " +\
			str(y) + " cm\n" +\
			"/InsertPic0 Do\n"+\
			"Q\n"
	else:
		S = ""
		NumberOfPicture = len(pictureorigin)
		for n in range(NumberOfPicture):
			w = picturesize[n][0]
			h = picturesize[n][1]
			x = pictureorigin[n][0]
			y = pictureorigin[n][1]
			S	+= "q\n" +\
				str(w) + " 0 0 " +\
				str(h) + " " +\
				str(x) + " " +\
				str(y) + " cm\n" +\
				"/InsertPic" + itos(n) + " Do\n"+\
				"Q\n"
	return S


def GetNumberOfListItem( what ):
	if isinstance (what, list) == False:
		return 1;
	return len(what)


global PDF_FilenameNumber
PDF_FilenameNumber = 0


def ResetPDF_FilenameNumber():
	global PDF_FilenameNumber
	PDF_FilenameNumber=0;
	return

def HTML_MinimalStartScript(w=100, h=100, color="#333"):
	print (color)
	EOL = "\n"
	S=	"<!DOCTYPE html>" + EOL +\
		"<html>" + EOL +\
		"<body>" +\
		"<canvas id=\"canvas\" "+\
		"width=\"" + str(w) + "\" height=\"" + str(h) +"\" "+\
		"style=\"background-color:"+color+"\"></canvas>"+ EOL +\
		"<script>" + EOL +\
		"var canvas = " +\
		"document.getElementById(\"canvas\");" +EOL +\
		"var " + CanvasContext +\
		" = canvas.getContext(\"2d\");" +EOL


	return S


def HTML_MinimalEndScript():
	EOL = "\n"
	return	"</script>"+EOL +\
			"</body>"+EOL +\
			"</html>"

def pt2px(pt):
	return 16*pt/12

def OrientationTransformation():
	S=""
	#S+= CanvasContextDot+\
	#	"translate(0,400);"+JavaEOL
	S+=scale(pt2px(1), pt2px(1))

	#flip horizontally
	#S+= scale(-1,1)
	return S



#Need to clean up a little bit.
#Clean up the a[".."] to make the makepdf more general.
def makepdf(GraphicsStream, Compress=False,
		InsertPicture = False,
		PictureFilename = [],
		UseJPEGForJPEGFile = False,
		#ImageData=[[128,128,128],[128,128,128],[34,70,24],[67,34,90]]):
		ImageData=[],
		ImageDataWidth =0,
		ImageDataHeigth =0,
		PaperSize="Letter",
		Unit="pt",
		PaperColor="white",
		ShowPDF=True,
		PDF_Viewer="open",
		PDF_Filename="killmex.pdf"):

	global PaperHeight
	PaperHeight = PaperSize[1]
	print (GraphicsStream)
	canvas_objects =[]
	canvas_objects += [HTML_MinimalStartScript(
						pt2px(PaperSize[0]),
						pt2px(PaperSize[1]),
						ToPSColor(PaperColor))]
	#Scale pt to px. 12 pt = 16 px
	canvas_objects += OrientationTransformation()
	canvas_objects += GraphicsStream
	canvas_objects += [HTML_MinimalEndScript()]


	if Compress:
		# in python 3, Zlib takes only Byte data. No more string.
		#GraphicsStream = gzip.compress(GraphicsStream)
		pass

	GotImageData = True if len(ImageData)>0 else False
	NumberOfImageData = 1 if GotImageData else 0

	if InsertPicture:
		pass
	else:
		if GotImageData:
			pass
		else:
			pass

	#Start to  insert picture from file
	if InsertPicture:
		pass




	if GotImageData:
		pass


	global PDF_FilenameNumber
	if PDF_FilenameNumber>0:
		pdf_filename = itos(PDF_FilenameNumber) + "_" +\
		 			PDF_Filename
	else:
		pdf_filename = PDF_Filename
	pdf_filename=pdf_filename[:-3] + "html"



	with open(pdf_filename, "w") as f:
		for x in canvas_objects:
			f.write(x)

	PDF_FilenameNumber +=1

	if ShowPDF:
		os.system("open" + " " + pdf_filename)

	return
