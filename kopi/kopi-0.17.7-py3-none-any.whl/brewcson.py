#!use python3
__all__ = ["brew_cson", "brew_multiplot_cson", "brew"]
from . import myglobal
def mystr(x):
	if isinstance(x, str):
		return "\"" + x + "\""
	elif isinstance(x, bool):
		if x ==True:
			return "true"
		else:
			return "false"
	elif isinstance(x, int):
		return str(x)
	else:
		return str(x)
GreetOne =(
	"# Preferences to adjust the appearance of a single plot\n" +
	"#\n"+
	"#\tFor the case of multi-subplot in a single graph,\n"+
	"#\tthe adjustment of subplots is controlled\n"+
	"#\tby another cson file, e.g. \"multiplotattrib.cson\"\n"+
	"#\tThe appearance of Each subplot is however,\n"+
	"#\tadjusted by this file.\n\n"+
	"#\tPS:\n"+
	"#\tStandard cson file does not have comments.\n"+
	"#\tThe comments are discarded before sending\n"+
	"#\tto the cson.loads\n"+
	"#\n"+
	"# \tSo far so good.\n")

GreetMulti =(
	"# Preferences to adjust the appearance of of multiplot\n" +
	"#\n"+
	"#\tThe appearance of Each subplot is however,\n"+
	"#\tadjusted by another cson file.\n")

Kopio ={
	"PDF":
		{
			"PDF_Filename"		:	"plotX.pdf",
			"ShowPDF"			:	True,
			"PDF_Viewer"		:	"open",
			"PDF_Compression"	:	False,
			"UseJPEGForJPEGFile":	False,
			"UseHTMLCanvas"		:	False
		},
	"Paper":
		{
			"Portrait" 	:	True,
			"Size"		: [500,400],
			"Unit"		: "pt",
			"Color" 	: ""
		},
	"PlotRange":
		{
			"Width"		: 300,
			"Height"	: 300,
			"Unit" 		: "pt" ,
			"AutoOrigin": True,
			"Origin"	: [60,50]
		},

	"Plot":
		{
			"LineColor"	: [ "black","red","blue","green"],
			"LineType"	: ["-","--"],
			"LineWidth"	: 1.5,
			"xlimit"	:[],
			"ylimit"	:[],
			"x2limit"	:[],
			"y2limit"	:[],
			"Point":
				{
				"Show"		:True,
				"Type"		:["SolidCircle","SolidSquare","SolidTriangle"],
				"Color"		:["red","blue","green"],
				"AutoSize"	:True,
				"SizeOverHeight":0.04,
				"Size"		:12,
				},
			"PlotBox":
				{
				"Show" 	: False,
				"BoxColor" : "gray",
				"LineWidth" : 1.0,
				"LineColor" : "black",
				"LineType" : "-",
				},
			"ErrorBar":
				{
				"Show": True,
				"Color": "blue",
				"LineWidth": 1,
				"AutoLength": True,
				"LengthOverWidth": 0.04,
				"Length" : 10
				},
		},
	"xLabel":{
		"Text"		: "Time (min)",
		"Font"		: "Helvetica",
		"OffsetX"	:0,
		"OffsetY"	:0,
		"AutoFontSize": True,
		"FontSizeOverHeight" : 0.06,
		"FontSize" : 14,
		"FontColor" : "blue"
		},
	"yLabel":
		{
		"Text":"Signal",
		"Font":"Helvetica",
		"OffsetX":0,
		"OffsetY":0,
		"AutoFontSize" : True,
		"FontSizeOverHeight":0.06,
		"FontSize" 	: 14,
		"FontColor" 	: "blue"
		},
	"Title":
		{
		"Show"	:	True,
		"Text"	:	"Title",
		"Font"	:	"Helvetica",
		"FontSize" : 14,
		"FontColor" : "black",
		"Alignment" : "l",
		"Spacing" : 0,
		"Yoffset" : 0,
		"Xoffset" : 0,
		"WidthRatio"	:	0.8,
		"AutoFontSize" : True,
		"FontSizeOverHeight" : 0.1
		},

	"Xaxis":
		{
		"ShowAxis"	: True,
		"LineWidth" : 1.5,
		"LineColor" : "black",
		"LineType" : "-",
		"ShowTickText" : True,
		"Yposition" : "",
		"YoffsetInPt":0,
		"Tick":
			{
			"Show" : True,
			"TickOut":True, #Tick "in" if false.
			"Length" : 3,	#If negative, tick to the opposite direction
			"Width" : 1.0,
			"Color" : "black",
			"Font" : "Helvetica",
			"FontSize" : 12,
			"FontColor" : "black",
			"AutoLength": True,
			"LengthOverHeight" : 0.03, #If negative, tick to the opposite direction
			"AutoFontSize": True,
			"FontSizeOverHeight": 0.05
			},
		"MinorTick":
			{
			"Show": True,
			"TickNumber"	: 5,
			"LineWidth" : 0.5,
			"LineColor" : "black",
			"LengthOverTickLength" : 0.6
			},
		"Grid":
			{
			"Show" : False,
			"LineColor" : "blue",
			"LineWidth" : 0.25,
			"LineType" : "-",
			},
		"MinorGrid":
			{
			"Show" : False,
			"LineColor" : "green",
			"LineWidth" : 0.1,
			"LineType" : "-"
			}
		},

	"Yaxis":
		{
		"ShowAxis" : True,
		"LineWidth" : 1.5,
		"LineColor" : "black",
		"LineType" : "-",
		"ShowTickText" :True,
		"Xposition" : "",
		"XoffsetInPt":0,
		"Tick":
			{
			"Show" : True,
			"TickOut": True, #Tick "in" if false.
			"Length" : 5, # Use this value if auto length is False
			"Width" : 1.0,
			"Color" : "black",
			"Font" : "Helvetica",
			"FontSize" : 12,
			"FontColor" : "black",
			"AutoLength" : True,
			"LengthOverHeight" : 0.03,
			"AutoFontSize" : True,
			"FontSizeOverHeight" : 0.05,
			"OffsetOfTextFromTickOverWidth" : 0.01
			},
		"MinorTick":
			{
			"Show" : True,
			"TickNumber"	: 5,
			"LineWidth" : 0.5,
			"LineColor" : "black",
			"LengthOverTickLength":0.6,
			},
		"Grid":
			{
			"Show" : False,
			"LineColor" : "blue",
			"LineWidth" : 0.25,
			"LineType" : "-"
			},
		"MinorGrid":
			{
			"Show" : False,
			"LineColor" : "green",
			"LineWidth" : 0.1,
			"LineType" : "-"
			}
		},

	"y2Label"	:	"Intensity2",
	"FillAreaUnderGraph"	:	False,
	"FillAreaColor"		:	["red","blue"],
	"Plot2Color"	:["red"],
	"BarChart"	: False,

	"Annotate" :[],
	"AnnotateFont" : "Helvetica",
	"AnnotateFontSize" : 8,
	"AnnotateFontColor" : "blue",
	"AnnotateWidth" : 100,
	"AnnotateAlignment" : 0,
	"AnnotateSpacing" :1,

	"Picture":
		{
		"InsertPicture"	:False,
		"PictureFilename" :["Example.jpg","PNG_example.png", "image1.jpg"],
		"PictureSize"	 :[[200,200],[100,100], [100,100]],
		"PictureOrigin"	:[[0,100],[200,100],[300,100]],
		"PictureCustom"	:True
		},

	"ShowDataOnly":False,

	"Debug":
		{
		"ShowErrorMessage":True,
		"ShowPrint":True,
		"VerbalEchoForMpretty":False,
		"EchoThisContent":False
		},
	"LogY"	:	False,
	"LogX"	:	False,
	"ColorMap":"viridis",
					# Available color map developed for
					# New matplotlib colormaps
					# by Nathaniel J. Smith, Stefan van der Walt,
					# and (in the case of viridis) Eric Firing:
					# Available colormap so far:
					# magma, inferno, plasma, viridis
	"SecondaryAxis":False

	}

Journal ={
	"PDF":
		{
			"PDF_Filename"		:	"plotX.pdf",
			"ShowPDF"			:	True,
			"PDF_Viewer"		:	"open",
			"PDF_Compression"	:	False,
			"UseJPEGForJPEGFile":	False,
			"UseHTMLCanvas"		:	False
		},
	"Paper":
		{
			"Portrait" 	:	True,
			"Size"		: [450,400],
			"Unit"		: "pt",
			"Color" 	: ""
		},
	"PlotRange":
		{
			"Width"		: 300,
			"Height"	: 300,
			"Unit" 		: "pt" ,
			"AutoOrigin": True,
			"Origin"	: [60,50]
		},

	"Plot":
		{
			"LineColor"	: "black",
			"LineType"	: ["-","--"],
			"LineWidth"	: 1,
			"xlimit"	:[],
			"ylimit"	:[],
			"x2limit"	:[],
			"y2limit"	:[],
			"Point":
				{
				"Show"		:True,
				"Type"		:["SolidCircle","SolidSquare","SolidTriangle"],
				"Color"		:"black",
				"AutoSize"	:False,
				"SizeOverHeight":0.04,
				"Size"		:10,
				},
			"PlotBox":
				{
				"Show" 	: False,
				"BoxColor" : "gray",
				"LineWidth" : 1.0,
				"LineColor" : "black",
				"LineType" : "-",
				},
			"ErrorBar":
				{
				"Show": True,
				"Color": "black",
				"LineWidth": 1,
				"AutoLength": True,
				"LengthOverWidth": 0.04,
				"Length" : 10
				},
		},
	"xLabel":{
		"Text"		: "Time (min)",
		"Font"		: "Helvetica",
		"OffsetX"	:0,
		"OffsetY"	:0,
		"AutoFontSize": False,
		"FontSizeOverHeight" : 0.06,
		"FontSize" : 14,
		"FontColor" : "black"
		},
	"yLabel":
		{
		"Text":"Signal",
		"Font":"Helvetica",
		"OffsetX":0,
		"OffsetY":0,
		"AutoFontSize" : False,
		"FontSizeOverHeight":0.06,
		"FontSize" 	: 14,
		"FontColor" 	: "black"
		},
	"Title":
		{
		"Show"	:	False,
		"Text"	:	"Title",
		"Font"	:	"Helvetica",
		"FontSize" : 14,
		"FontColor" : "black",
		"Alignment" : "l",
		"Spacing" : 0,
		"Yoffset" : 0,
		"Xoffset" : 0,
		"WidthRatio"	:	0.8,
		"AutoFontSize" : True,
		"FontSizeOverHeight" : 0.1
		},

	"Xaxis":
		{
		"ShowAxis"	: True,
		"LineWidth" : 1,
		"LineColor" : "black",
		"LineType" : "-",
		"ShowTickText" : True,
		"Yposition" : "",
		"YoffsetInPt":0,
		"Tick":
			{
			"Show" : True,
			"TickOut":True, #Tick "in" if false.
			"Length" : 3,	#If negative, tick to the opposite direction
			"Width" : 1.0,
			"Color" : "black",
			"Font" : "Helvetica",
			"FontSize" : 12,
			"FontColor" : "black",
			"AutoLength": True,
			"LengthOverHeight" : 0.03, #If negative, tick to the opposite direction
			"AutoFontSize": True,
			"FontSizeOverHeight": 0.05
			},
		"MinorTick":
			{
			"Show": False,
			"TickNumber"	: 5,
			"LineWidth" : 0.75,
			"LineColor" : "black",
			"LengthOverTickLength" : 0.6
			},
		"Grid":
			{
			"Show" : False,
			"LineColor" : "blue",
			"LineWidth" : 0.25,
			"LineType" : "-",
			},
		"MinorGrid":
			{
			"Show" : False,
			"LineColor" : "green",
			"LineWidth" : 0.1,
			"LineType" : "-"
			}
		},

	"Yaxis":
		{
		"ShowAxis" : True,
		"LineWidth" : 1,
		"LineColor" : "black",
		"LineType" : "-",
		"ShowTickText" :True,
		"Xposition" : "",
		"XoffsetInPt":0,
		"Tick":
			{
			"Show" : True,
			"TickOut": True, #Tick "in" if false.
			"Length" : 5, # Use this value if auto length is False
			"Width" : 1.0,
			"Color" : "black",
			"Font" : "Helvetica",
			"FontSize" : 12,
			"FontColor" : "black",
			"AutoLength" : True,
			"LengthOverHeight" : 0.03,
			"AutoFontSize" : False,
			"FontSizeOverHeight" : 0.05,
			"OffsetOfTextFromTickOverWidth" : 0.01
			},
		"MinorTick":
			{
			"Show" : False,
			"TickNumber"	: 5,
			"LineWidth" : 0.75,
			"LineColor" : "black",
			"LengthOverTickLength":0.6,
			},
		"Grid":
			{
			"Show" : False,
			"LineColor" : "blue",
			"LineWidth" : 0.25,
			"LineType" : "-"
			},
		"MinorGrid":
			{
			"Show" : False,
			"LineColor" : "green",
			"LineWidth" : 0.1,
			"LineType" : "-"
			}
		},

	"y2Label"	:	"Intensity2",
	"FillAreaUnderGraph"	:	False,
	"FillAreaColor"		:	["red","blue"],
	"Plot2Color"	:["red"],
	"BarChart"	: False,

	"Annotate" :[],
	"AnnotateFont" : "Helvetica",
	"AnnotateFontSize" : 8,
	"AnnotateFontColor" : "blue",
	"AnnotateWidth" : 100,
	"AnnotateAlignment" : 0,
	"AnnotateSpacing" :1,

	"Picture":
		{
		"InsertPicture"	:False,
		"PictureFilename" :["Example.jpg","PNG_example.png", "image1.jpg"],
		"PictureSize"	 :[[200,200],[100,100], [100,100]],
		"PictureOrigin"	:[[0,100],[200,100],[300,100]],
		"PictureCustom"	:True
		},

	"ShowDataOnly":False,

	"Debug":
		{
		"ShowErrorMessage":True,
		"ShowPrint":True,
		"VerbalEchoForMpretty":False,
		"EchoThisContent":False
		},
	"LogY"	:	False,
	"LogX"	:	False,
	"ColorMap":"viridis",
					# Available color map developed for
					# New matplotlib colormaps
					# by Nathaniel J. Smith, Stefan van der Walt,
					# and (in the case of viridis) Eric Firing:
					# Available colormap so far:
					# magma, inferno, plasma, viridis
	"SecondaryAxis":False

	}


HelpKopio ={
	"PDF":
		{
			"PDF_Filename"		:	"\t# The file name to store the plotted pdf file. Default : \"plotX.pdf\"\n",
			"ShowPDF"			:	"\t# Open the pdf viewer when the plot file is ready. Default: True\n",
			"PDF_Viewer"		:	"\t# Default in Mac: \"open\"\n",
			"PDF_Compression"	:	"\t# E.g.: false\n",
			"UseJPEGForJPEGFile":	"\t# E.g.: false\n",
			"UseHTMLCanvas"		:	"\t# E.g.: false\n",
		},
	"Paper":
		{
			"Portrait" 	: "\t# true for portrait and false for landscape. Default: true\n",
			"Size"		: "\t# [width, height] for the pdf paper. Defalt: [500,400]\n",
			"Unit"		: "\t# only pt is stable\n",
			"Color" 	: "\t# leave it \"\" for white color\n"
		},
	"PlotRange":
		{
			"Width"		: "\t# Plot width in pt. Default : 300\n",
			"Height"	: "\t# Plot heigth in pt. Default : 300\n",
			"Unit" 		: "\t# so far only \"pt\" is stable\n",
			"AutoOrigin": "\t# True for auto, False for manual\n",
			"Origin"	: "\t# This will be used for manual origin. Default: [60,50]\n"
		},

	"Plot":
		{
			"LineColor"	: 	"\t# Accept verbal name or HTML color code\n"+\
							"\t# e.g. [\"black\",\"red\",\"blue\"] for multiple lines\n"+\
							"\t# or [#000000, #FF0000, #0000FF]\n"+\
							"\t# or just \"black\" for single line\n",

			"LineType"	:	"\t# Available linetype:\n"+\
							"\t# \"\":\tno line\n"+\
							"\t# \"-\":\tnormal continuous line\n"+\
							"\t# \"--\":\tdashed line\n"+\
							"\t# \".\":\tdotted line\n"+\
							"\t# \"-.-\"\t:dashed dotted dashed line\n"+\
							"\t# E.g.: [\"-\",\"--\"]for multiple line\n"+\
							"\t# Also accept custom line type defination in pdf format\n"+\
							"\t# e.g. [[10,20],0]\n",
			"LineWidth"	: 	"\t# In pt. Default: 1.5\n",
			"xlimit"	:	"\t# The range to be plotted. E.g. [xmin, xmax]. Auto: []\n",
			"ylimit"	:	"\t# E.g. [ymin, ymax]. Auto: []\n",
			"x2limit"	:	"\t# For second axis. E.g. [xmin, xmax]. Auto: []\n",
			"y2limit"	:	"\t# For second axis. E.g. [xmin, xmax]. Auto: []\n",
			"Point":
				{
				"Show"		: 		"\t\t# Set true to draw points\n"+\
									"\t\t# Also accept List. E.g. [true, true, false] for multiplot\n",
				"Type"		:		"\t\t# E.g.: \"SolidCircle\",\"SolidSquare\",\"SolidTriangle\"]\n",
				"Color"		:		"\t\t# E.g.: [\"red\",\"blue\",\"green\"]\n",
				"AutoSize"	:		"\t\t# E.g.: true\n",
				"SizeOverHeight": 	"\t\t# Height_of_point/Height_of_plot. Default: 0.04\n",
				"Size"		: 		"\t\t# This value will be used if AuotoSize is false\n",
				},
			"PlotBox":
				{
				"Show" 	: 		"\t\t# Set true to color the background. Default: false\n",
				"BoxColor" :	"\t\t# E.g.: \"gray\"\n",
				"LineWidth" :	"\t\t# Line width in pt. E.g.: 1.0",
				"LineColor" :	"\t\t# E.g.: \"black\"\n",
				"LineType" :	"\t\t# E.g.: \"-\"\n",
				},
			"ErrorBar":
				{
				"Show": 			"\t\t# Set true to draw error bar. Default: false\n",
				"Color": 			"\t\t# Color of the error bar\n",
				"LineWidth": 		"\t\t# Default: 1.0\n",
				"AutoLength": 		"\t\t# Set true to auto adjust the error bars\n",
				"LengthOverWidth": 	"\t\t# Length of the error bar/Plot width. Default: 0.05\n",
				"Length" : 			"\t\t# This value will be used if AuotoLength is false. Default: 10\n",
				},
		},
	"xLabel":{
		"Text"		: 	"\t# The label for x axis\n",
		"Font"		:	"\t# The name of the font. E.g.: Helvetica\n",
		"OffsetX"	:	"\t# Offset in pt in x-direction\n"+\
						"\t# Adjust this value to move the xlabel horizontally\n",
		"OffsetY"	:	"\t# Offset in pt in x-direction\n"+\
						"\t# Adjust this value to move the xlabel vertically\n",

		"AutoFontSize": 		"\t# Default : true\n",
		"FontSizeOverHeight" : 	"\t# Heigth_font/Height_plot. E.g. : 0.06\n",
		"FontSize" : 			"\t# This value will be used if AuotoFontSize is false. E.g. 12\n",
		"FontColor" : 			"\t# E.g.: \"black\"\n",
		},
	"yLabel":
		{
		"Text":					"\t# The label for y axis\n",
		"Font":					"\t# The name of the font. E.g.: Helvetica\n",
		"OffsetX":				"\t# Offset in pt in x-direction\n"+\
								"\t# Adjust this value to move the ylabel vertically\n",
		"OffsetY":				"\t# Offset in pt in y-direction\n"+\
								"\t# Adjust this value to move the ylabel vertically\n",
		"AutoFontSize" : 		"\t# Default : true\n",
		"FontSizeOverHeight":	"\t# Heigth_font/Height_plot. E.g. : 0.06\n",
		"FontSize" 	: 			"\t# This value will be used if AuotoFontSize is false. E.g. 12\n",
		"FontColor" 	: 		"\t# E.g.: \"black\"\n",
		},
	"Title":
		{
		"Show"	:				"\t# Set true to show title\n",
		"Text"	:				"\t# The text for the Title\n",
		"Font"	:				"\t# The name of the font. E.g.: Helvetica\n",
		"FontSize" : 			"\t# This value will be used if AuotoFontSize is false. E.g. 14\n",
		"FontColor" : 			"\t# E.g.: \"black\"\n",
		"Alignment" : 			"\t# \"l\" for align to the left\n",
		"Spacing" : 			"\t# I dont know !\n",
		"Yoffset" : 			"\t# Offset in pt in y-direction\n",
		"Xoffset" : 			"\t# Offset in pt in x-direction\n",
		"WidthRatio": 			"\t# I dont know !. Defult: 0.8\n",
		"AutoFontSize": 		"\t# Default : true\n",
		"FontSizeOverHeight" : 	"\t# Heigth_font/Height_plot. E.g. : 0.1\n"
		},

	"Xaxis":
		{
		"ShowAxis"	:	"\t# Default : true\n",
		"LineWidth" :	"\t# axis line width in pt. E.g.: 1.5\n",
		"LineColor" :	"\t# E.g. \"black\"\n",
		"LineType" :	"\t# Default: \"-\"\n",
		"ShowTickText":	"\t# Default: true",
		"Yposition":	"\t# Y-position to put the Xaxis\n"+\
						"\t# Use the unit in your graph\n"+\
						"\t# E.g.: \"\" for auto\n" +\
						"\t# E.g.: 10.0 for drawing X-axis at y=10",
		"YoffsetInPt":	"\t# Shift Xaxis vertically. Unit in pt",

		"Tick":
			{
			"Show" : 				"\t\t# Set true to draw the tick\n",
			"TickOut":				"\t\t# Tick \'out\' if true, tick \'in\' if false\n",
			"Length" :				"\t\t# E.g.: 3. If negative, tick to the opposite direction\n",
			"Width" :				"\t\t# E.g.: 1.0\n",
			"Color" :				"\t\t# E.g.: \"black\"\n",
			"Font" :				"\t\t# E.g.: \"Helvetica\"\n",
			"FontSize" :			"\t\t# E.g.: 12\n",
			"FontColor" : 			"\t\t# E.g. \"black\"\n",
			"AutoLength": 			"\t\t# E.g. true\n",
			"LengthOverHeight":		"\t\t# E.g.: 0.03. If negative, tick to the opposite direction\n",
			"AutoFontSize":			"\t\t# Default: true\n",
			"FontSizeOverHeight":	"\t\t# E.g.: 0.05\n"
			},
		"MinorTick":
			{
			"Show": 				"\t\t# Set true to display the minor tick\n",
			"TickNumber" : 			"\t\t# E.g.: 5. \n"+\
									"\t\t# It is actually the number to step from major tick to another\n",
			"LineWidth" : 			"\t\t# E.g.: 0.5\n",
			"LineColor" : 			"\t\t# E.g. \"black\"\n",
			"LengthOverTickLength":	"\t\t# MinorTickLength/MajorTickLength. E.g.: 0.6\n"
			},
		"Grid":
			{
			"Show" : 		"\t\t# Set true to display the grid for the major tick\n",
			"LineColor" : 	"\t\t# E.g. \"blue\"\n",
			"LineWidth" : 	"\t\t# E.g.: 0.25\n",
			"LineType" : 	"\t\t# E.g. \"-\"\n",
			},
		"MinorGrid":
			{
			"Show" : 		"\t\t# Set true to display the grid for the minor tick\n",
			"LineColor" : 	"\t\t# E.g.: \"green\"\n",
			"LineWidth" : 	"\t\t# E.g.: 0.1\n",
			"LineType" : 	"\t\t# E.g. \"-\"\n",
			}
		},

	"Yaxis":
		{
		"ShowAxis"	:	"\t# Default : true\n",
		"LineWidth" : 	"\t# axis line width in pt. E.g.: 1.5\n",
		"LineColor" : 	"\t# E.g. \"black\"\n",
		"LineType" : 	"\t# Default: \"-\"\n",
		"ShowTickText":	"\t# Default: true",
		"Xposition":	"\t# X-position to put the Yaxis\n"+\
						"\t# Use the unit in your graph\n"+\
						"\t# E.g.: \"\" for auto\n" +\
						"\t# E.g.: 10.0 for drawing Y-axis at x=10",
		"XoffsetInPt":	"\t# Shift Yaxis horizontally. Unit in pt",

		"Tick":
			{
			"Show" : 							"\t\t# Set true to draw the tick\n",
			"TickOut":							"\t\t# Tick \'out\' if true, tick \'in\' if false\n",
			"Length" :							"\t\t# E.g.: 3. If negative, tick to the opposite direction\n",
			"Width" :							"\t\t# E.g.: 1.0\n",
			"Color" :							"\t\t# E.g.: \"black\"\n",
			"Font" :							"\t\t# E.g.: \"Helvetica\"\n",
			"FontSize" :						"\t\t# E.g.: 12\n",
			"FontColor" : 						"\t\t# E.g. \"black\"\n",
			"AutoLength": 						"\t\t# E.g. true\n",
			"LengthOverHeight" : 				"\t\t# E.g.: 0.03. If negative, tick to the opposite direction\n",
			"AutoFontSize": 					"\t\t# Default: true\n",
			"FontSizeOverHeight": 				"\t\t# E.g.: 0.05\n",
			"OffsetOfTextFromTickOverWidth":	"\t\t# Distance from the y-tick/ Plot width. E.g: 0.01\n"
			},
		"MinorTick":
			{
			"Show": 					"\t\t# Set true to display the minor tick\n",
			"TickNumber" : 				"\t\t# E.g.: 5. \n"+\
										"\t\t# It is actually the number to step from major tick to another\n",
			"LineWidth" : 				"\t\t# E.g.: 0.5\n",
			"LineColor" : 				"\t\t# E.g. \"black\"\n",
			"LengthOverTickLength" :	"\t\t# MinorTickLength/MajorTickLength. E.g.: 0.6\n"
			},
		"Grid":
			{
			"Show" : 		"\t\t# Set true to display the grid for the major tick\n",
			"LineColor" : 	"\t\t# E.g. \"blue\"\n",
			"LineWidth" : 	"\t\t# E.g.: 0.25\n",
			"LineType" : 	"\t\t# E.g. \"-\"\n",
			},
		"MinorGrid":
			{
			"Show" : 		"\t\t# Set true to display the grid for the minor tick\n",
			"LineColor" : 	"\t\t# E.g.: \"green\"\n",
			"LineWidth" : 	"\t\t# E.g.: 0.1\n",
			"LineType" : 	"\t\t# E.g. \"-\"\n",
			}
		},

	"y2Label"	:	"\t# Label for secondary y-axis\n",
	"FillAreaUnderGraph"	:"\t# E.g. False\n",
	"FillAreaColor"		:	"\t# E.g.: [\"red\",\"blue\"]\n",
	"Plot2Color"	: 	"\t# E.g.: [\"red\"]\n",
	"BarChart"	: 		"\t# Default: False",

	"Annotate" :			"\t# Not available yet. E.g. []\n",
	"AnnotateFont" : 		"\t# E.g. \"Helvetica\"\n",
	"AnnotateFontSize" : 	"\t# E.g.: 8\n",
	"AnnotateFontColor" : 	"\t# E.g.: \"blue\"\n",
	"AnnotateWidth" : 		"\t# I dont know\n",
	"AnnotateAlignment" : 	"\t# I dont know\n",
	"AnnotateSpacing" :		"\t# I dont know\n",

	"Picture":
		{
		"InsertPicture"	: 	"\t# Set true to insert JPG picture as the background",
		"PictureFilename" :	"\t# Valid filename or a list of filenames for the picture\n"+\
							"\t# E.g.: [\"Example.jpg\",\"PNG_example.png\", \"image1.jpg\"]\n",
		"PictureSize"	 :	"\t# E.g.: [[200,200],[100,100], [100,100]]\n",
		"PictureOrigin"	:	"\t# E.g.: [[0,100],[200,100],[300,100]]\n",
		"PictureCustom"	:	"\t# Not sure what it is\n"
		},

	"ShowDataOnly":"\t# Set true to draw curve only. No axes, title, label etc. Default: false\n",

	"Debug":
		{
		"ShowErrorMessage": 	"\t# Not available yet\n",
		"ShowPrint": 			"\t# Not available yet\n",
		"VerbalEchoForMpretty":	"\t# Not available yet\n",
		"EchoThisContent":		"\t# Not available yet\n",
		},
	"LogY"	:	"\t# Set true to use Log scale for Y-axis\n",
	"LogX"	:	"\t# Set true to use Log scale for X-axis\n",
	"ColorMap":	"\t# E.g. \"viridis\""+\
				"\t# Available color map developed for\n"+\
				"\t# New matplotlib colormaps\n"+\
				"\t# by Nathaniel J. Smith, Stefan van der Walt\n"+\
				"\t# and (in the case of viridis) Eric Firing:\n"+\
				"\t# Available colormap so far:\n"+\
				"\t# magma, inferno, plasma, viridis\n",
	"SecondaryAxis": "\t# Default: False\n"

	}


MultiPlotBasic={
	"PaperSize":[600,600],
	"Height":400,
	"Width":400,
	"RowColumn":[2,2],
	"AutoOrigin":True,
	"Origin":[50,50],
	"Origins":[[50,100],[200,100]],
	"AutoAdjust":True,
	#{}"HeightToWidthRatioThreshold":1
	"RowSpacing":60,	# in pt
	"ColumnSpacing":60,
	"SubPlotHeight":[100, 100],
	"SubPlotWidth": [100, 100],
	"PDF_Compression":True,
	"InsertPicture"			:False,
	"PictureFilename"		:["Example.jpg","PNG_example.png", "image1.jpg"],
	"PictureSize"		:[[200,200],[100,100], [100,100]],
	"PictureOrigin"			:[[0,100],[200,100],[300,100]],
	"UseJPEGForJPEGFile"	:False
	}
HelpMultiPlot={
	"PaperSize":		"# E.g: [600,600]\n",
	"Height":			"# E.g: 400\n",
	"Width":			"# E.g: 400\n",
	"RowColumn":		"# E.g: [2,2]\n",
	"AutoOrigin":		"# E.g: true\n",
	"Origin":			"# E.g: [50,50\n",
	"Origins":			"# E.g: [[50,100],[200,100]]\n",
	"AutoAdjust":		"# E.g: true\n",
	"RowSpacing":		"# E.g: 60  in pt\n",
	"ColumnSpacing":	"# E.g: 60\n",
	"SubPlotHeight":	"# E.g: [100, 100]\n",
	"SubPlotWidth": 	"# E.g: [100, 100]\n",
	"PDF_Compression": 	"# E.g: True\n",
	"InsertPicture":	"# E.g: False\n",
	"PictureFilename":	"# E.g:[\"Example.jpg\",\"PNG_example.png\", \"image1.jpg\"]\n",
	"PictureSize":		"# E.g.: [[200,200],[100,100], [100,100]]\n",
	"PictureOrigin"	:	"# E.g: [[0,100],[200,100],[300,100]]\n",
	"UseJPEGForJPEGFile": "# E.g: False\n"
}


def brew(what = "", filename = myglobal.DEFAULT_PLOTSTYLE_FILENAME):
	cappuccino = Kopio
	if what == "":
		pass
	elif what == "all":
		cappuccino = Kopio
		cappuccino["Xaxis"]["Grid"]["Show"]=True
		cappuccino["Yaxis"]["Grid"]["Show"]=True
		cappuccino["Xaxis"]["MinorGrid"]["Show"]=True
		cappuccino["Yaxis"]["MinorGrid"]["Show"]=True
	elif what == "journal":
		cappuccino = Journal


	createcson(filename, cappuccino, GreetOne, HelpKopio)
	return

def HelpMessage(H):
	#if not isinstance(H, str):
	#	print("\a Here........")
	#	print (H)
	#	return "#" + mystr(H) + "\n"
	return H + "\n"

def createcson(filename, D, Welcome, H):
	S=""
	f = open(filename, 'w')
	S += Welcome
	#H = Help
	for x in D:
		if isinstance(D[x], dict):
			S += str(x) + ":\n"
			for y in D[x]:
				if isinstance(D[x][y], dict):
					S += "\t"+ str(y) + ":\n"
					for z in D[x][y]:
						S += "\t\t" +\
						 	str(z) +\
							 ": " +\
							 mystr(D[x][y][z]) +\
							 "\n"
						S += HelpMessage(H[x][y][z])
				else:
					S += "\t" + str(y) +\
					 ": " + mystr(D[x][y]) + "\n"
					S += HelpMessage(H[x][y])
		else:
			S += str(x) + ": " + mystr(D[x]) + "\n"
			S += HelpMessage(H[x])

	f.write(S)
	print("Default plot_style.cson created.")
	f.close()

def brew_cson(coffeename):
	createcson(coffeename, Kopio, GreetOne, HelpKopio)
	return
def brew_multiplot_cson(coffeename):
	createcson(coffeename, MultiPlotBasic, GreetMulti, HelpMultiPlot)
	return
