"""
	Collection of small modules to handle pdf script
"""

import numpy as np
from datetime import datetime
import os
import zlib as gzip
from .misc import *
from .myfont import GetStringWidth, ShortFontName
from .myimage import *
#from .font import ShortFontName

from .mycolor import *

# Data in pdf are written in Bytes

# Global Variable for Making  PDF
CurrentRGB_Stroking= [0,0,0]
CurrentRGB_NonStroking= [0,0,0]
CurrentLineWidth= 0
CurrentDash = [[],0]
CurrentRotateAngle = 0
CurrentLineJoin= "miter"
CurrentFont= ""
CurrentFontSize= 0

def RGBtoPostScriptRGB(StandardRGB = [255, 255, 255]):#{{{
	# PostScript or PDF takes rgb value from 0 to 1.0 instead of 0 to 255
	PostScriptRGB = np.array([1.0, 1.0, 1.0])
	PostScriptRGB[0] = 1.0*StandardRGB[0]/255
	PostScriptRGB[1] = 1.0*StandardRGB[1]/255
	PostScriptRGB[2] = 1.0*StandardRGB[2]/255
	return PostScriptRGB#}}}

def ToPSColor(Color="black"):
	#If Verbal color contain something, then use that as color
	if Color == "Pattern":
		return Color

	Standard_RGB =  ColorNameToRGB(Color)
	PostScript_RGB = ([1.0, 1.0, 1.0])
	PostScript_RGB[0] = 1.0*Standard_RGB[0]/255
	PostScript_RGB[1] = 1.0*Standard_RGB[1]/255
	PostScript_RGB[2] = 1.0*Standard_RGB[2]/255

	return PostScript_RGB

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

def translate(tx, ty):
	return "1 0 0 1 " + str(tx) + " " + str(ty) + " cm\n"

def lineto(x, y):
	return (ftos(x) + " " + ftos(y) + " l\n")

def moveto(x, y):
	return (ftos(x) + " " + ftos(y) + " m\n")

def stroke():
	return "S\n"

def close():
	return "h\n"

def close_stroke():
	return "s\n"

def fill():
	return "f\n"

def close_fill_only():
	return "h\n" + "f\n"

def fill_stroke():
	return "B\n"

def close_fill_stroke():
	return "b\n"

def close_shade():
	return "W n q \n" + "/S1 sh Q\n"
	#return "h /S1 sh\n"

def set_pattern():
	return "/Pattern cs\n"+\
			"/P1 scn\n"

def rectangle(x,y,width, height):
	return (ftos(x) +" " + ftos(y) + " " +\
			ftos(width) + " " + ftos(height) + " re\n")

def curveto(x1, y1, x2, y2, x3, y3):
	return ftos(x1) + " " + ftos(y1) + " " +\
			ftos(x2) + " " + ftos(y2) + " " +\
			ftos(x3) + " " +ftos(y3) + " c\n"

def setlinewidth(linewidth):
	global CurrentLineWidth
	if linewidth == CurrentLineWidth:
		return ""
	CurrentLineWidth = linewidth
	return (ftos(linewidth) + " w\n")

def setdash(pdf_DashArray, pdf_DashOffset):
	global CurrentDash
	if (pdf_DashArray == CurrentDash[0] ) and\
	(pdf_DashOffset) == CurrentDash[1]:
		return ""
	CurrentDash[0] = pdf_DashArray
	CurrentDash[1] = pdf_DashOffset
	List0=""
	for n in range(len (pdf_DashArray)):
		List0 += ftos(pdf_DashArray[n])
		if n < (len(pdf_DashArray) -1):
			List0 += " "
	return ("[" + List0 + "] " + ftos(pdf_DashOffset) + " d\n")

def setlinejoin(JoinType="miter"):
	global CurrentLineJoin
	if JoinType == CurrentLineJoin:
		return ""
	CurrentLineJoin = JoinType
	S = ""
	if JoinType == "miter":
		S += "0"
	elif JoinType == "round":
		S += "1"
	elif JoinType == "bevel":
		S += "2"
	else:
		S += "0"
	return (S + " j\n")

def setrgb_stroking(pdf_rgb):
	#pdf_rgb is normalized RGB in pdf format
	#Maximum value is 1 instead of 255
	global CurrentRGB_Stroking
	if pdf_rgb == CurrentRGB_Stroking:
		return ""
	CurrentRGB_Stroking = pdf_rgb
	return (ftos(pdf_rgb[0]) + " " +\
					ftos(pdf_rgb[1]) + " " +\
					ftos(pdf_rgb[2]) + " RG\n")

def setrgb_nonstroking(pdf_rgb):
	global CurrentRGB_NonStroking
	if pdf_rgb == CurrentRGB_NonStroking:
		return ""
	CurrentRGB_NonStroking = pdf_rgb
	return (ftos(pdf_rgb[0]) + " " +\
			ftos(pdf_rgb[1]) + " " +\
			ftos(pdf_rgb[2]) + " rg\n")

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
	#S=""
	#S +=	("[] 0 d\n" +\
	#	"0 0 0 RG\n" +
	#	"0 0 0 rg\n" +\
	#	"0 j\n" +\
	#	"1 w\n")
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

	f = ShortFontName[font]
	return ("/" + f + " " + ftos(fontsize) + " Tf\n")

def text_position(x ,y):
	return ftos(x) + " " + ftos(y) + " Td\n"

def show_text(text):
	return "(" + text + ") Tj\n"

def setrotate(angle_degree):
	radian = np.pi*1.0*angle_degree/180
	return 	ftos6( np.cos(radian) ) +\
			" " + ftos6( np.sin(radian) ) + " " +\
		ftos6(-1*np.sin(radian) ) +\
		" " + ftos6(np.cos(radian)) + " 0 0 cm\n"

def gsave():
	return "q\n"

def grestore():
	return "Q\n"

def DrawLine(x1, y1, x2, y2,
		linewidth=1, pdf_rgb=[0,0,0], pdf_dash=[[],0]):

	S=""
	S+= (	setlinewidth(linewidth) +
		setdash(pdf_dash[0], pdf_dash[1]) +
		setrgb_stroking(pdf_rgb))
	S+= (moveto(x1,y1) + lineto(x2, y2))
	S+= stroke()
	return S

def DrawLines(xa, ya, linewidth, linejoin, pdf_RGB, pdf_Dash):
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

def PutErrorBar(xa, ya, uppererror, lowererror, length, rgb, linewidth ):
	S =""
	if(len(xa))>1:
		for i in range(len(xa)):
			x1 = xa[i]
			x2 = x1
			y1 = ya[i] + uppererror[i]
			y2 = ya[i] - lowererror[i]
			S += DrawLine(x1, y1, x2, y2,
				linewidth, pdf_rgb=rgb)
			S += DrawLine(x1-length/2, y1, x1+length/2, y1,
				linewidth, pdf_rgb=rgb)
			S += DrawLine(x1-length/2, y2, x1+length/2, y2,
				linewidth, pdf_rgb=rgb)
	return S

def PutText(x, y, text, font, fontsize, rgb, rotation, alignment):

	#	Defination for Alignment:
	#	 XXx
	#	^	this is the default [0,0,], Bottom-Left Aligned
	#	 XXx
	#	  ^	this is [0.5, 0]  Bottom-Center Aligned
	#	 XXx
	#	   ^	this is [1,0] 	Right-Aligned
	#	Same rules applied to Verical Axis.
	#	eg:
	#	_
	#	 XXx	this is [0,1] Upper-Left Aligned
	#	   _
	#	 XXx	this is [1,1) Upper-Roght Aligned.
	#
	#	However, FontSize and the actual font height are not exactly equal,
	#	so, some fine tuning needs to be done to give perfect alignemnt effect.

	stringwidth=GetStringWidth(text, font, fontsize)
	text=InsertEscapeBeforeParenthesis(text)
	S=""
	S +=  translate(x, y)

	if rotation !=0:
		S += setrotate(rotation)

	S += "BT\n"
	S += (	setrgb_nonstroking(rgb) +
		selectfont(font, fontsize) )

	S += text_position(0, 0)

	if (alignment[0]!= 0) | (alignment[1] !=0 ):
		xoffset = -1.0 * alignment[0] * stringwidth
		yoffset = -1.0 * alignment[1] * fontsize
		S += text_position(xoffset, yoffset)

	S += show_text(text)
	S += "ET\n"

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

#--------------------------------------------------------

def obj_definefont(ObjectNumber,
					GenerationNumber,
					BaseFont,
					DefineFontName):
	S = str(ObjectNumber) + " " + str(GenerationNumber) + " obj\n"
	S += ("<</Type /Font\n"+
		"/Subtype /Type1\n"+
		"/Name /" + DefineFontName + "\n"+
		"/BaseFont /"+ BaseFont +"\n"+
		#"/Encoding /MacRomanEncoding\n"+
		#"/Encoding /WinAnsiEncoding\n"+
		">>\n"+
		"endobj\n"
	)
	return S.encode()

def obj_greeting():
	S =""
	S +=	"%PDF-1.4\n"+\
			"% Created Manually\n"+\
			"%%Creator: Lee Chuin CHEN\n" +\
			"%% [leechuin@yamanashi.ac.jp, leechuin@gmail.com]\n" +\
			"%%Title: pplot\n" +\
			"%%CreationDate: "+ str(datetime.now()) + "\n"
	return S.encode()

def obj_catalog (objnum_base, objnum_outlines, objnum_pages):
	S = str(objnum_base) + " 0 obj\n"+\
		"<</Type /Catalog\n" +\
		"/Outlines " + str(objnum_outlines) + " 0 R\n" +\
		"/Pages " + str(objnum_pages) +" 0 R\n" +\
		">>\n" +\
		"endobj\n"
	return S.encode()

def obj_outline(objnum_outlines):
	S = str(objnum_outlines) + " 0 obj\n" +\
		"<</Type /Outlines\n" +\
		"/Count 0\n" +\
		">>" +\
		"endobj\n"
	return S.encode()

def obj_pages(objnum_pages, objnum_kids):
	#{{{
	S = str(objnum_pages) + " 0 obj\n" +\
		"<</Type /Pages\n" +\
		"/Kids [" + str(objnum_kids) + " 0 R]\n" +\
		"/Count 1\n" +\
		">>\n" +\
		"endobj\n"
	return S.encode()

def obj_pagetype(objnum_kids,
		objnum_pages,
		objnum_fontbase,
		objnum_contents,
		objnum_picture=0,
		objnum_dataimage=0,
		objnum_pattern = 0,
		objnum_shading= 0,
		PaperSize="Letter",
		Unit="pt",
		InsertPicture=False,
		PictureFilename=[]
		):
	#DeclareFont = [	["FH"	,	fontname.Helvetica],
	#					["FHB"	,	fontname.Helvetica_Bold],
	#					...
	DeclaredFont = ShortFontName.items()
	S_AllFontnames= ""
	S_Xobject = ""
	S_Pattern = ""
	S_Shading = ""

	FontPointer = objnum_fontbase
	S_Pattern = "/Pattern << /P1 " + str(objnum_pattern) + " 0 R >>\n"
	S_Shading = "/Shading << /S1 " + str(objnum_shading) + " 0 R >>\n"

	GotDataImage = True if objnum_dataimage!=0 else 0
	if InsertPicture | GotDataImage :
		S_Xobject += "/XObject <<\n"
		if InsertPicture:
			NumberOfPicture = GetNumberOfListItem(PictureFilename)
			for n in range(NumberOfPicture):
				S_Xobject +=\
				"/InsertPic" + itos(n) + " " +\
				str(objnum_picture + n ) +\
				" 0 R\n"
		if GotDataImage:
			S_Xobject +=\
				"/DataImg0" + " " +\
				str(objnum_dataimage) +\
				" 0 R\n"
		S_Xobject += ">>\n"
	#e.g : /FT 40 0 R
	for f in DeclaredFont:
		S_AllFontnames += "/" + f[1] + " " + str(FontPointer) + " 0 R\n"
		FontPointer = FontPointer + 1
	S = (str(objnum_kids) + " 0 obj\n" +\
		"<</Type /Page\n" +\
		"/Parent " + str(objnum_pages) + " 0 R\n" +\
		#The code to adjust the paper size
		#"/MediaBox [0 0 612 792]\n" +
		"/MediaBox [0 0 " +\
		GetPaperSize(PaperSize,Unit) + "]\n"+\
		"/Contents " + str(objnum_contents) + " 0 R\n" +\
		"/Resources<</ProcSet [/PDF /Text]\n"+\
		"/Font <<\n"+\
			S_AllFontnames+\
		">>\n"+\
		S_Xobject +\
		S_Pattern +\
		S_Shading +\
		">>\n"+\
		">>\n"+\
		"endobj\n")
	return S.encode()

def obj_endstream_endobj():
	return 	("\n"+
			"endstream\n"+
			"endobj\n").encode()

def obj_contents(objnum_contents, Stream, Compress):
	#The Stream here is Byte
	StreamLength = len(Stream)
	S = str(objnum_contents) + " 0 obj\n" +\
			"<< /Length %d "%StreamLength +"\n"+\
			("/Filter /FlateDecode" if Compress else "") +\
			">>\n"+\
			"stream\n"
	return S.encode()+\
	 		Stream +\
		 	obj_endstream_endobj()

def obj_image(objnum_picture, ImageWidth,
		ImageHeight, ImageStream, DCTDecode):
	ImageLength = len(ImageStream)
	S=	str(objnum_picture) + " 0 obj\n" +\
		"<< /Type /XObject\n"+\
		"/Subtype /Image\n"+\
		"/Width " + str(ImageWidth) + "\n" +\
		"/Height " + str(ImageHeight) + "\n" +\
		"/ColorSpace /DeviceRGB\n"+\
		"/BitsPerComponent 8\n"+\
		"/Length "+ str(ImageLength) + "\n"+\
		"/Filter ["+\
				"/FlateDecode "+\
				"/ASCIIHexDecode "+\
				("/DCTDecode" if DCTDecode else "") +\
				"] >>\n"+\
		"stream\n"
	return S.encode()+\
			ImageStream+\
			obj_endstream_endobj()

def obj_pattern(objnum_pattern, Scaling = 1):
	Box = 20
	dBox = 2
	PatternStream =	(
		"BT\n"+
		"/FH 1 Tf\n"+\
		"64 0 0 64 7.1771 2.4414 Tm 0 Tc\n"+\
		"0 Tw\n"+\
		"1.0 0.0 0.0 rg\n"+\
		"(A) Tj\n"+\
		"0.7478 -0.007 TD\n"+\
		"0.0 1.0 0.0 rg\n"+\
		"(B) Tj\n"+\
		"-0.7323 0.7813 TD\n"+\
		"0.0 0.0 1.0 rg\n"+\
		"(D) Tj\n"+\
		"0.6913 0.007 TD\n"+\
		"0.0 0.0 0.0 rg\n"+\
		"(E) Tj\n"+
		"ET\n")
	Pattern2 = (
			moveto(0,0) +
			lineto(100,100)+
			stroke()
			)

	Pattern3 = DrawLine(0, 0, Box, Box,
		linewidth=1, pdf_rgb=[1,0,0], pdf_dash=[[],0])

	Pattern4 = DrawLine(0, Box, Box, 0,
		linewidth=1, pdf_rgb=[0,1,0], pdf_dash=[[],0])

	Pattern5 = DrawLine(0, Box/2, Box, Box/2,
		linewidth=1, pdf_rgb=[1,0,0], pdf_dash=[[],0])

	Pattern=Pattern4+Pattern3
	S=""
	S += (str(objnum_pattern) + " 0 obj\n"+
		"<< /Type /Pattern\n"+
		"/PatternType 1\n"+
		"/PaintType 1\n"+
		"/TilingType 2\n"+
		"/BBox [0 0 " + str(Box) + " " + str(Box) + "]\n"+
		"/XStep "+ str(Box- dBox) + "\n"+
		"/YStep "+ str(Box- dBox) + "\n"+
		"/Resources <</Font <</FH 10 0 R>>\n>>\n"+
		"/Matrix [" + str(Scaling) +
		" 0.0 0.0 " + str(Scaling) + " 0.0 0.0]\n"+
		"/Length "+ str(len(Pattern)) +"\n"+
		">>\n"+
		"stream\n"+
		#PatternStream +
		Pattern+
		"endstream\nendobj\n"
		)
	return S.encode()

def obj_shading(objnum_shading, Scaling = 1):
	Box = 20
	dBox = 2
	S=""
	S += (str(objnum_shading) + " 0 obj\n"+
		"<< /Type /Pattern\n"+
		"/PatternType 2\n"+
		"/ShadingType 2\n"+
		"/ColorSpace /DeviceRGB\n"+
		">>\n"+
		"endobj\n"
		)
	return S.encode()

def obj_xref(pdf_objects):
	#{{{
	# At last, about time to write the XREF
	# If it is not done correctly, some pdf reader
	#eg. GS will complaint.:(
	NumOfPdfObj = len(pdf_objects)
	offset = [0]*NumOfPdfObj
	for i in range(1, NumOfPdfObj):
		offset[i] = offset[i-1] + len(pdf_objects[i-1])

	startxref = offset[NumOfPdfObj-1] + len(pdf_objects[NumOfPdfObj -1])

	Xref=""
	for i in range(1 , NumOfPdfObj):
		Xref += Decimal_To_10_DigitsString(offset[i]) + " 00000 n\r\n"

	pdf_xref = ("xref\r\n"+
		"0 "+ str(NumOfPdfObj) +" \r\n"+
		"0000000000 65535 f\r\n"+
		Xref +
		"trailer\n"+
		"<</Size 8\n"+
		"/Root 1 0 R\n"+
		">>\n"+
		"startxref\n"+
		"%d"%(startxref) + "\n"
		"%%%EOF\n")
	return pdf_xref.encode()

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

	GraphicsStream=GraphicsStream.encode()
	GotImageData = True if len(ImageData)>0 else False
	NumberOfImageData = 1 if GotImageData else 0
	if Compress:
		# in python 3, Zlib takes only Byte data. No more string.
		GraphicsStream = gzip.compress(GraphicsStream)

	# Manually assignig pdf obj number
	objnum_base 	= 1
	objnum_outlines	= objnum_base + 1
	objnum_pages	= objnum_outlines + 1
	objnum_kids		= objnum_pages + 1
	objnum_contents = objnum_kids + 1


	objnum_picture = 0
	objnum_dataimage = 0
	if InsertPicture:
		objnum_picture	= objnum_contents + 1
		NumberOfPicture = GetNumberOfListItem(
							PictureFilename )
		if GotImageData:
			objnum_dataimage =\
			 	objnum_picture + NumberOfPicture
			objnum_pattern = objnum_dataimage + 1
		else:
			objnum_pattern =\
			 	objnum_picture + NumberOfPicture
	else:
		if GotImageData:
			objnum_dataimage= objnum_contents + 1
			objnum_pattern = objnum_dataimage + 1
		else:
			objnum_pattern = objnum_contents + 1

	objnum_shading = objnum_pattern + 1
	objnum_fontbase = objnum_shading + 1

	# Start writing pdf objects
	NumOfPdfObj = 1
	pdf_objects = []
	pdf_objects.append(obj_greeting())

	pdf_objects.append(obj_catalog (
						objnum_base,
						objnum_outlines,
						objnum_pages
						)
					)

	pdf_objects .append(
		 obj_outline(objnum_outlines)
		)

	pdf_objects.append(
		obj_pages(	objnum_pages,
					objnum_kids)
			)

	pdf_objects.append(
		obj_pagetype(
			objnum_kids,
			objnum_pages,
			objnum_fontbase,
			objnum_contents,
			objnum_picture if InsertPicture else 0,
			objnum_dataimage,
			objnum_pattern,
			objnum_shading,
			PaperSize,
			Unit,
			InsertPicture,
			PictureFilename,
			)
		)

	pdf_objects.append(obj_contents(objnum_contents,
						GraphicsStream,
						Compress ))

	#Start to  insert picture from file
	if InsertPicture:
		NumberOfPicture = GetNumberOfListItem(PictureFilename)
		for n in range(NumberOfPicture):
			[imagewidth,
			imageheight,
			imagelength,
			imagestream] = [0,0,0,"".encode()]
			ImageFilename = Drink(PictureFilename ,n)
			DCTDecode =\
			 	True if IsJPGFile(ImageFilename) &\
				UseJPEGForJPEGFile else False

			RetrievedImageData =\
			 		GetImageByteStreamFromFile(
					ImageFilename,
					DCTDecode
					)
			if RetrievedImageData == -1:
				PrintError(
					"Can not get image stream for \"" +
					ImageFilename + "\"")
			else:
				[imagestream,
				imagewidth,
				imageheight]  =	RetrievedImageData

			pdf_objects.append(
				obj_image(
						(objnum_picture + n),
						imagewidth,
						imageheight,
						imagestream,
						DCTDecode
						)
				)

	if GotImageData:
		imagestream = GetImageByteStreamFromData(
			ImageData)
		pdf_objects.append(
				obj_image(
						(objnum_dataimage),
						ImageDataWidth,
						ImageDataHeigth,
						imagestream,
						False
						)
				)

	pdf_objects.append(
			obj_pattern(objnum_pattern)
			)
	pdf_objects.append(
			obj_shading(objnum_shading)
			)

	DeclareFont = ShortFontName.items()
	# Insert all available fonts
	FontPointer = objnum_fontbase
	for f in DeclareFont:
		pdf_objects.append(
				obj_definefont( FontPointer,
								0,
								f[0],	# Full name
								f[1]	# Short name
								)
				)
		FontPointer = FontPointer +  1

	#Finally, time to write the xref
	pdf_xref = obj_xref(pdf_objects)
	global PDF_FilenameNumber
	if PDF_FilenameNumber>0:
		pdf_filename = itos(PDF_FilenameNumber) + "_" +\
		 			PDF_Filename
	else:
		pdf_filename = PDF_Filename

	with open(pdf_filename, "wb") as TargetFile:
		for myobject in pdf_objects:
			TargetFile.write(myobject)
		TargetFile.write(pdf_xref)
	PDF_FilenameNumber +=1

	if ShowPDF:
		os.system(PDF_Viewer + " " + pdf_filename)

	return
