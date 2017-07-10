
import cairo as Cairo
import math
import logging, os

#from gi.repository import Gtk, Gdk, GLib, Pango
#from gi.repository.GdkPixbuf import Pixbuf, InterpType
import cairo
#import matplotlib.pyplot as plt

#======================================================================	
def draw_test():

	Width, Height = 400, 250
	output = "./GUI/images/circle.png"

	surf = Cairo.ImageSurface(Cairo.FORMAT_RGB24,Width,Height)
	Ctx = Cairo.Context(surf)

	# fill everything with white
	Ctx.new_path()
	Ctx.set_source_rgb(0.9,0.9,0.9)
	Ctx.rectangle(0,0,Width,Height)
	Ctx.fill()  # fill current path

	# display text in the center
	Ctx.set_source_rgb(0,0,0)  # black
	txt = "Hello, Matthieu !"
	Ctx.select_font_face("Ubuntu", Cairo.FONT_SLANT_NORMAL, Cairo.FONT_WEIGHT_NORMAL)
	Ctx.set_font_size(18)
	x_off, y_off, tw, th = Ctx.text_extents(txt)[:4]
	Ctx.move_to(Width/2-x_off-tw/2,Height/2-y_off-th/2)
	Ctx.show_text(txt)

	# draw a circle in the center
	Ctx.new_path()
	Ctx.set_source_rgb(0,0.2,0.8)  # blue
	Ctx.arc(Width/2,Height/2,tw*0.6,0,2*pi)
	Ctx.stroke()  # stroke current path

	# save to PNG
	surf.write_to_png(output)
	return output

#======================================================================	
class Drawing:
#----------------------------------------------------------------------
	def __init__(self, Ctx=None):
		self.Ctx = Ctx
		
#----------------------------------------------------------------------
	def App(self, ImagePath, ParamDict, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("no context to draw (Drawing.App)")
			return False
				
		#--------------------------------------------------
		if ImagePath!=None:
			
#			# Save graph image and display it on canvas
#			plt.figure().patch.set_alpha(0)
#			plt.subplot(111)
#			position = nx.spring_layout(CTG,iterations=100)
#	#		# Initialize position of init nodes
#	#		for InitServ in filter(lambda x: x.Type=="Input", position.keys()): 
#	#			position[InitServ][0]=0
#			nx.draw(CTG,node_color='c',node_size=1000,with_labels=True,width=3, pos=position)
#			plt.savefig(ParamDict["Name"]+".png")
#			#plt.show()
		
			if os.path.isfile(ImagePath): 
				PixB=Pixbuf.new_from_file(ImagePath)
				YStart = 30*Ratio+5
				W, H = PixB.get_width()+5, PixB.get_height()+YStart+5
				
				# Fill everything with blue gradient
				Sx, Sy = max(Width, int(W)), max(Height, int(H))
#				DefaultBG(self.Ctx, Sx, Sy)
				
				Gdk.cairo_set_source_pixbuf(self.Ctx, PixB, 0, YStart)
				self.Ctx.paint()
				DrawApp(self.Ctx, ParamDict["Name"], x=Width, y=Height, Ratio=Ratio)
				return W, H
		#--------------------------------------------------
		
		# Fill everything with blue gradient
#		DefaultBG(self.Ctx, Width, Height)
		
		W, H = DrawApp(self.Ctx, ParamDict["Name"], x=Width, y=Height, Ratio=Ratio)
		return W, H
		
#----------------------------------------------------------------------
	def Algo(self, ImagePath, ParamDict, Width=600, Height=400, Ratio=1):
		"""
		Draw on specified context algorithm representation.
		"""
		if(not self.Ctx): 
			logging.error("no context to draw (Drawing.App)")
			return False
		#--------------------------------------------------
		if ImagePath!=None:
			if os.path.isfile(ImagePath): 
				PixB=Pixbuf.new_from_file(ImagePath)
				YStart = 30*Ratio+5
				W, H = PixB.get_width()+5, PixB.get_height()+YStart+5
				
				# Fill everything with blue gradient
				Sx, Sy = max(Width, int(W)), max(Height, int(H))
#				DefaultBG(self.Ctx, Sx, Sy)
				
				Gdk.cairo_set_source_pixbuf(self.Ctx, PixB, 0, YStart)
				self.Ctx.paint()
				DrawAlgo(self.Ctx, ParamDict["Name"], x=Width, y=Height, Ratio=Ratio)
				return W, H 
		#--------------------------------------------------
		# fill everything with blue gradient
#		DefaultBG(self.Ctx, Width, Height)
		W, H = DrawAlgo(self.Ctx, ParamDict["Name"], x=Width, y=Height, Ratio=Ratio)
		return W, H

#----------------------------------------------------------------------
	def Arch(self, ParamDict, FPGAMatrix, PortList, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("no context to draw on (Drawing.Arch)")
			return False
		# fill everything with blue gradient
#		DefaultBG(self.Ctx, Width, Height)
		W, H = DrawArch(self.Ctx, ParamDict["Name"], FPGAMatrix, PortList, x=0, y=0, Width=Width, Height=Height, Ratio=Ratio)
		return W, H

#----------------------------------------------------------------------
	def FPGA(self, ParamDict, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("no context to draw on (Drawing.FPGA)")
			return

		# fill everything with blue gradient
#		DefaultBG(self.Ctx, Width, Height)

		x0 = 10 
		y0 = 10

		W, H = DrawFPGA(self.Ctx, ParamDict, x0, y0, Width=Width, Height=Height, Ratio=Ratio)

		return W, H

#----------------------------------------------------------------------
	def Port(self, ParamDict, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("no context to draw on (Drawing.Port)")
			return

		# Fill everything with blue gradient
#		DefaultBG(self.Ctx, Width, Height)

		# Define where to draw
		x0 = 20 
		y0 = 20

		W, H = DrawPort(self.Ctx, ParamDict, x0, y0, Width=Width, Height=Height, Ratio=Ratio)

		return W, H

#----------------------------------------------------------------------
	def NoC(self, ParamDict, IPMatrix, Width=600, Height=400, Selected=(-1,-1), Ratio=1):
		if(not self.Ctx): 
			logging.error("[Drawing.NoC] no context to draw on.")
			return
						
		# Draw square NoC representation
		x, y = IPMatrix.Size()
		
		IPSize     = 100*Ratio
		RouterSize = 50*Ratio
		IPSpace    = 30*Ratio
		NodeSize   = (IPSize+RouterSize/2)
		
		W, H = (NodeSize)*x+10+IPSpace*(x-1), (NodeSize)*y+10+IPSpace*(y-1)
		
		# Fill everything with blue gradient
		Sx, Sy = max(Width, int(W)), max(Height, int(H))
#		DefaultBG(self.Ctx, Sx, Sy)
		
		for (i, j), NodeIP in IPMatrix.BrowseMatrix():
			# Set xmax, ymax so as to avoid arrows at the borders
			if IPMatrix.Get(i+1, j)==None: LnR=False
			else: LnR=True
			if IPMatrix.Get(i, j+1)==None: LnUp=False
			else: LnUp=True
				
			if NodeIP!=None:
				IPParameters=NodeIP.Parameters["Common"].copy()
				IPParameters.update(NodeIP.Parameters["Parent"])
				IPParameters.update(NodeIP.Parameters["Resources"])
				SelX, SelY = Selected
				DrawNode(self.Ctx, i, j, y-1, IPParameters, LinkRight=LnR, LinkUp=LnUp, Selected=(SelX==i and SelY==j), Ratio=Ratio)
			else:
				IPParameters={"Name":"IP ?"}
				DrawNode(self.Ctx, i, j, y-1, IPParameters, LinkRight=LnR, LinkUp=LnUp, Ratio=Ratio)

		return W, H

#----------------------------------------------------------------------
	def IP(self, ParamDict, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("[Drawing.IP] no context to draw.")
			return False

		IPWidth, IPHeight = 400*Ratio, 400*Ratio 
		x0, y0 = 20, 20
		# First fill everything with blue gradient
		Sx, Sy = max(Width, int(IPWidth+x0))+5, max(Height, int(IPHeight+y0))+5
#		DefaultBG(self.Ctx, Sx, Sy)
		W, H = DrawIP(self.Ctx, ParamDict, x=x0, y=y0, Width=Width, Height=Height, Ratio=Ratio, Compact=False)

		return W, H

#----------------------------------------------------------------------
	def Lib(self, ParamDict, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("[Drawing.Lib] no context to draw.")
			return False
		# Fill everything with blue gradient
#		DefaultBG(self.Ctx, Width, Height)
		W, H = DrawLib(self.Ctx, ParamDict, x=20, y=20, Width=Width, Height=Height, Ratio=Ratio)
		return W, H
#----------------------------------------------------------------------
	def GetSelected(self, x, y, ymax, Type=None, Ratio=1.0):
		if Ratio==0: return -1, -1
		if Type=="NoC":
			IPSpace=30*Ratio
			x=(x-IPSpace)/Ratio
			y=(y-IPSpace)/Ratio
			
			RouterX = int(x/100)
			RouterY = ymax-int(y/100)
			return RouterX, RouterY
			
		elif Type=="Architecture":
			FPGASpace=30*Ratio
			x=(x-FPGASpace)/Ratio
			y=(y-FPGASpace)/Ratio 
			
			FPGAX = int(x/100)
			FPGAY = ymax-int(y/100)
			return FPGAX, FPGAY
#----------------------------------------------------------------------
	def BackGround(self, Width=600, Height=400):
		"""
		Fill everything with blue gradient
		"""
		if(not self.Ctx): 
			logging.error("[Drawing.BackGround] no context to draw.")
			return False
		DefaultBG(self.Ctx, Width, Height)

#======================================================================	
def DrawIP(Ctx, ParamDict, x=20, y=20, Width=400, Height=400, Ratio=1, Compact=False, Selected=False):
	"Draw a FPGA in the specified context to x, y location."
	#logging.debug("Display '{0}'".format(ParamDict["Name"]))
	PinLength = 20*Ratio
	PinSpace  = 20*Ratio
	FontSize  = 20*Ratio
	
	# Get Title width/height
	Title='{0}'.format(ParamDict["Name"])
	TitleFont = 20*Ratio
	LetterWidth = Ctx.text_extents("O")[:4][3]
	while(1):
		Ctx.set_font_size(TitleFont)
		x_off, y_off, tw, th = Ctx.text_extents(Title)[:4]
		if tw+LetterWidth < 200*Ratio: break
		else: TitleFont*=0.95
	
	TitleHeight = th
	PinMargin = TitleHeight	
	
	if not Compact: 
		try: 
			#Extract signal names
#			Signals=map(lambda x: x.split('/'), ParamDict["Ports"])
#			NI=map(lambda x: x.split('/'), ParamDict["NetworkInterface"])
#			Resets=map(lambda x: x.split('/')[0], ParamDict["Resets"])
#			Clocks=map(lambda x: x.split('/')[0], ParamDict["Clocks"])
#			
#			Inputs  = map(lambda x: x[0], filter(lambda x: x[1].upper()=="IN", Signals))
#			Outputs = map(lambda x: x[0], filter(lambda x: x[1].upper()=="OUT", Signals))
#			NIInputs  = map(lambda x: x[0], filter(lambda x: x[1].upper()=="IN", NI))
#			NIOutputs = map(lambda x: x[0], filter(lambda x: x[1].upper()=="OUT", NI))

			######## NEW VERSION ##############
			IOMappings=list(ParamDict["Ports"].values())
			NI=ParamDict["NetworkInterface"]
			Resets=ParamDict["Resets"]
			Clocks=ParamDict["Clocks"]
		
			Inputs  = [x.Signal.Name for x in [x for x in IOMappings if x.Signal.Dir.upper()=="IN"]]
			Outputs = [x.Signal.Name for x in [x for x in IOMappings if x.Signal.Dir.upper()=="OUT"]]
			NIInputs  = [x.Name for x in [x for x in NI if x.Dir.upper()=="IN"]]
			NIOutputs = [x.Name for x in [x for x in NI if x.Dir.upper()=="OUT"]]

			# Determine the maximal width of 
			PortsWidth = ( max(list(map(len, Inputs+NIInputs)))+max(list(map(len, Outputs+NIOutputs))) )*LetterWidth+50
		except: PortsWidth = 0;Inputs = []; Outputs=[];NIInputs = [];NIOutputs = []
		IPWidth  = max(200*Ratio, tw+PinSpace, PortsWidth) 
		MaxPorts, MaxNI = max(len(Inputs), len(Outputs)), max(len(NIInputs), len(NIOutputs))
		PortHeight = PinSpace*(MaxPorts)+2*PinMargin+2*FontSize
		NIHeight   = PinSpace*(MaxNI)+2*FontSize
		IPHeight = max(200*Ratio, PortHeight+NIHeight)
		Margin = PinLength
	else: 
		IPWidth  = 200*Ratio
		IPHeight = 200*Ratio
		Margin = 0
	x0, y0 = (x+Margin, y+Margin)

	# Then draw the IP body
	Ctx.set_line_width(1)
	Ctx.set_source_rgba(0.0, 0.3, 0.5, 0.8); # blue (a bit transparent)
	Ctx.rectangle(x0, y0, IPWidth, IPHeight)
	Ctx.fill(); # Fill first

	# Display IP name at TOP of the square
	Ctx.set_source_rgba(1,1,1)  # Write in White
	if Compact: TitleYPos = y0+IPHeight/2
	else: TitleYPos = (y0+TitleHeight)-y_off-th/2
	DrawText(Ctx, x0+IPWidth/2, TitleYPos,
			Text=Title, Color="White", Align="Center", Bold=False, 
			FontSize=TitleFont, Opacity=1)
	#Ctx.move_to((x0+LetterWidth)-x_off,(y0+TitleHeight)-y_off-th/2)
	#Ctx.show_text(Title) 
	# Draw bold boundaries
	Ctx.set_line_width(2)
	if Selected:  Ctx.set_source_rgba(0.8, 0.2, 0.2, 0.8); # Red (a bit transparent)
	else: Ctx.set_source_rgba(0.0, 0.0, 0.3, 1) # Blue (opaque)
	Ctx.rectangle(x0, y0, IPWidth, IPHeight)
	Ctx.stroke();
	
	if not Compact:
		# Display IOs
		Ctx.set_line_width(1)
		Ctx.set_font_size(FontSize-2)
		for i in range(0, len(Inputs)): # Inputs
			Ctx.set_source_rgba(0, 0, 0, 1) # Black
			Ctx.move_to(x0-PinLength, y0+PinSpace*i+PinMargin+2*FontSize)
			DrawArrow(Ctx, x0, y0+PinSpace*i+PinMargin+2*FontSize, Start=False, End=True)
			#Ctx.line_to(x0, y0+PinSpace*i+PinMargin+2*FontSize)
			Ctx.stroke(); 
			# Display pin names within the frame
			Text=Inputs[i]
			Ctx.set_source_rgba(0.9,0.9,0.8, 1)  # Write in light orange
			x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
			Ctx.move_to((x0+5)-x_off,(y0+2*FontSize+PinSpace*i+PinMargin)-y_off-th/2)
			Ctx.show_text(Text)
		for i in range(0, len(NIInputs)): # Inputs
			Ctx.set_source_rgba(0, 0, 0, 1) # Black
			Ctx.move_to(x0-PinLength, y0+PinSpace*(i+MaxPorts)+3*PinMargin+2*FontSize)
			DrawArrow(Ctx, x0, y0+PinSpace*(i+MaxPorts)+3*PinMargin+2*FontSize, Start=False, End=True)
			#Ctx.line_to(x0, y0+PinSpace*i+PinMargin+2*FontSize)
			Ctx.stroke(); 
			# Display pin names within the frame
			Text=NIInputs[i]
			Ctx.set_source_rgba(0.9,0.9,0.8, 1)  # Write in light orange
			x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
			Ctx.move_to((x0+5)-x_off,(y0+2*FontSize+PinSpace*(i+MaxPorts)+3*PinMargin)-y_off-th/2)
			Ctx.show_text(Text)
		for i in range(0, len(Outputs)): # Outputs
			Ctx.set_source_rgba(0, 0, 0, 1) # Black
			Ctx.move_to(x0+IPWidth, y0+PinSpace*i+PinMargin+2*FontSize)
			DrawArrow(Ctx, x0+IPWidth+PinLength, y0+PinSpace*i+PinMargin+2*FontSize, Start=False, End=True)
			#Ctx.line_to(x0+IPWidth+PinLength, y0+PinSpace*i+PinMargin+2*FontSize)
			Ctx.stroke(); 
			# Display pin names within the frame
			Text=Outputs[i]
			Ctx.set_source_rgba(0.9,0.9,0.8, 1)  # Write in light orange
			x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
			Ctx.move_to((x0+IPWidth-tw-5)-x_off,(y0+2*FontSize+PinSpace*i+PinMargin)-y_off-th/2)
			Ctx.show_text(Text)
		for i in range(0, len(NIOutputs)): # Outputs
			Ctx.set_source_rgba(0, 0, 0, 1) # Black
			Ctx.move_to(x0+IPWidth, y0+PinSpace*(i+MaxPorts)+3*PinMargin+2*FontSize)
			DrawArrow(Ctx, x0+IPWidth+PinLength, y0+PinSpace*(i+MaxPorts)+3*PinMargin+2*FontSize, Start=False, End=True)
			#Ctx.line_to(x0+IPWidth+PinLength, y0+PinSpace*i+PinMargin+2*FontSize)
			Ctx.stroke(); 
			# Display pin names within the frame
			Text=NIOutputs[i]
			Ctx.set_source_rgba(0.9,0.9,0.8, 1)  # Write in light orange
			x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
			Ctx.move_to((x0+IPWidth-tw-5)-x_off,(y0+2*FontSize+PinSpace*(i+MaxPorts)+3*PinMargin)-y_off-th/2)
			Ctx.show_text(Text)
		# Draw separator between port and NI
		Ctx.set_source_rgba(0, 0, 0, 1) # Black
		Ctx.move_to(x0, y0+PinSpace*(MaxPorts)+2*PinMargin+2*FontSize)
		Ctx.line_to(x0+IPWidth, y0+PinSpace*(MaxPorts)+2*PinMargin+2*FontSize)
		# Draw text = PORTS
		DrawText(Ctx, x0+IPWidth/2, 
				y0+PortHeight-2,
				Text="PORTS", 
				Align="Center", 
				Bold=True, 
				FontSize=15*Ratio, 
				Opacity=1)
		# Draw text = NETWORK INTERFACE
		DrawText(Ctx, x0+IPWidth/2, 
				y0+IPHeight-2,
				Text="NETWORK INTERFACE", 
				Align="Center", 
				Bold=True, 
				FontSize=15*Ratio, 
				Opacity=1)
		Ctx.stroke()
	
	return  IPWidth+x0, IPHeight+y0

#======================================================================	
def DrawLib(Ctx, ParamDict, x=20, y=20, Width=400, Height=400, Ratio=1):
	"Display information about the library."
	
	# First fill everything with blue gradient
#	DefaultBG(Ctx, Width, Height)
	
	#logging.debug("Display '{0}'".format(ParamDict["Name"]))
	FontSize = 16*Ratio

	# Display lib name
	Ctx.move_to(x*2, 0)
	Ctx.line_to(x*2, y)
	Ctx.stroke(); 
	W, H = DrawText(Ctx, x/2, 30*Ratio, Text=ParamDict["Name"], Color="Black", Align="Left", Bold=True, FontSize=16*Ratio, Opacity=1)
	return x, y+H

#======================================================================	
def DrawNode(Ctx, i, j, jmax, ParamDict, LinkRight=True, LinkUp=True, Selected=False, Ratio=1):
	IPRatio    = 0.5*Ratio
	IPSize     = 100*Ratio
	RouterSize = 50*Ratio
	FontSize   = 15*Ratio
	IPSpace    = 30*Ratio
	x0r, y0r   = (IPSize*0.75, IPSize*0.75)
	
	x0, y0 = 5+i*(IPSize+IPSpace), 5+(jmax-j)*(IPSize+IPSpace) # x0 and y0 are the origins of the draw
	
	DrawIP(Ctx, ParamDict, x=x0, y=y0, Ratio=IPRatio, Compact=True, Selected=Selected)
	
	# Draw the router
	Ctx.set_line_width(0.5);
	Ctx.set_source_rgba(0.8, 0.5, 0.1, 1) # Orange (opac)
	Ctx.rectangle(x0+x0r, y0+y0r, RouterSize, RouterSize)
	Ctx.fill()

	# Display router address in the center of the router
	RoutAddr = "R{0}{1}".format(i,j)
	Ctx.set_source_rgba(1,1,1)  # Write in White
	Ctx.set_font_size(FontSize)
	x_off, y_off, tw, th = Ctx.text_extents(RoutAddr)[:4]
	Ctx.move_to((x0+x0r+RouterSize/2)-x_off-tw/2,(y0+y0r+RouterSize/2)-y_off-th/2)
	Ctx.show_text(RoutAddr)

	# Now draw the links between routers
	#logging.debug("Now draw the links between routers")
	Ctx.set_line_width(1)
	Ctx.set_source_rgba(0, 0, 0, 1) # Black
	
	HLength = 80*Ratio # Distance between two routers
	VLength = 75*Ratio # Distance between two routers
	if LinkRight:
		dx, dy = IPSize+RouterSize/2, IPSize+IPSpace/2
		Ctx.move_to(x0+dx, y0+dy)
		DrawArrow(Ctx, x0+dx+HLength, y0+dy, Start=True, End=True) # Horizontal
	#move_to(x0, y0)
	if LinkUp:
		dx, dy = IPSize+IPSpace/2, RouterSize/2-IPSpace
		Ctx.move_to(x0+dx, y0+dy)
		DrawArrow(Ctx, x0+dx, y0+VLength, Start=True, End=True) # Vertical
	Ctx.stroke()
	
	return x0+x0r+RouterSize, y0+y0r+RouterSize

#======================================================================	
def DrawPort(Ctx, ParamDict, x=20, y=20, Width=400, Height=400, Ratio=1):
	"Display information about the application."
	# First fill everything with blue gradient
#	DefaultBG(Ctx, Width, Height)
	#logging.debug("Display '{0}'".format(ParamDict["Name"]))
	FontSize = 16*Ratio

	# Display port name
	Ctx.move_to(x*2, 0)
	Ctx.line_to(x*2, y)
	Ctx.stroke(); 
	W, H = DrawText(Ctx, x/2, 30*Ratio, Text=ParamDict["Name"], Color="Black", Align="Left", Bold=True, FontSize=16*Ratio, Opacity=1)
	return x, y+H

#======================================================================	
def DrawFPGA(Ctx, ParamDict, x=20, y=20, Width=400, Height=400, Ratio=1):
	"Draw a FPGA in the specified context to x, y location."
	#logging.debug("Display '{0}'".format(ParamDict["Name"]))
	FPGAWidth, FPGAHeight = 200*Ratio, 200*Ratio
	PinLength = 20*Ratio
	PinSpace  = 20*Ratio
	Margin    = 20*Ratio
	PinMargin = 10*Ratio
	x0, y0 = (x+Margin, y+Margin)
	
	TotalW, TotalH =  x0+FPGAWidth+2*PinLength, y0+FPGAHeight+2*PinLength

	# First fill everything with blue gradient
#	Sx, Sy = max(Width, int(TotalW))+5, max(Height, int(TotalH))+5
#	DefaultBG(Ctx, Sx, Sy)
	
	
	# First draw the chip body
	Ctx.set_line_width(1)
	Ctx.set_source_rgba(0.0, 0.8, 0.2, 1) # Green (opaque)
	Ctx.rectangle(x0, y0, FPGAWidth, FPGAHeight)
	Ctx.fill(); # Fill first

	# Display FPGA pins
	Ctx.set_line_width(4)
	Ctx.set_source_rgba(0.476, 0.236, 0, 1) # Dark orange (238 118 0)
	for i in range(0, 10): # Top
		Ctx.move_to(x0+PinSpace*i+PinMargin, y0)
		Ctx.line_to(x0+PinSpace*i+PinMargin, y0-PinLength)
	for i in range(0, 10): # Bottom
		Ctx.move_to(x0+PinSpace*i+PinMargin, y0+FPGAHeight)
		Ctx.line_to(x0+PinSpace*i+PinMargin, y0+FPGAHeight+PinLength)
	for i in range(0, 10): # Left
		Ctx.move_to(x0, y0+PinSpace*i+PinMargin)
		Ctx.line_to(x0-PinLength, y0+PinSpace*i+PinMargin)
	for i in range(0, 10): # Right
		Ctx.move_to(x0+FPGAWidth, y0+PinSpace*i+PinMargin)
		Ctx.line_to(x0+FPGAWidth+PinLength, y0+PinSpace*i+PinMargin)
	Ctx.stroke(); 

	Ctx.set_source_rgba(0.0, 0.3, 0.0, 1) # Green (opaque)
	Ctx.rectangle(x0, y0, FPGAWidth, FPGAHeight)
	Ctx.stroke(); # then Draw bold boundaries
	

	# Display FPGA name in the center of the router
	Ctx.select_font_face("Ubuntu", Cairo.FONT_SLANT_NORMAL, Cairo.FONT_WEIGHT_NORMAL)
	Ctx.set_source_rgba(1,1,1)  # Write in White
	Ctx.set_font_size(15*Ratio)
	x_off, y_off, tw, th = Ctx.text_extents(ParamDict["Brand"])[:4]
	Ctx.move_to((x0+FPGAWidth/2)-x_off-tw/2,(y0+FPGAHeight/2-FPGAHeight*0.15)-y_off-th/2)
	Ctx.show_text(ParamDict["Brand"])
	x_off, y_off, tw, th = Ctx.text_extents(ParamDict["Family"])[:4]
	Ctx.move_to((x0+FPGAWidth/2)-x_off-tw/2,(y0+FPGAHeight/2+FPGAHeight*0)-y_off-th/2)
	Ctx.show_text(ParamDict["Family"])
	x_off, y_off, tw, th = Ctx.text_extents(ParamDict["Name"])[:4]
	Ctx.move_to((x0+FPGAWidth/2)-x_off-tw/2,(y0+FPGAHeight/2+FPGAHeight*0.15)-y_off-th/2)
	Ctx.show_text(ParamDict["Name"])
	
	return TotalW, TotalH

#======================================================================	
def DrawArch(Ctx, ArchName, FPGAMatrix, PortList, x=20, y=20, Width=400, Height=400, Ratio=1):
	"Draw a board populated with FPGAs in the specified context to x, y location."
	#logging.debug("Display '{0}'".format(ArchName))
	NBPORTS=len(PortList)
	if NBPORTS: xBoard, yBoard = 60*Ratio, 0
	else: xBoard, yBoard = 0, 0
	XMargin  = xBoard+33*Ratio # From border to board shape
	YMargin  = yBoard+33*Ratio # From border to board shape
	FMargin = 10*Ratio # From board edge to FPGA pins
	FRatio=0.8*Ratio
	FWidth, FHeight = 240*FRatio, 240*FRatio # FPGA size = 240
	Space = 0
	FontSize = 16*Ratio
	NbRows, NbColumn = FPGAMatrix.Size()
	Xsize, Ysize = NbRows*FWidth, NbColumn*FHeight
	PortBoxSize = 40*Ratio
	PortSpace   = 10*Ratio
	BWIDTH, BHEIGHT = Xsize+2*FMargin, max(Ysize+2*FMargin, (NBPORTS-1)*(PortBoxSize+PortSpace)+PortBoxSize/3)
	
	TotalW, TotalH = XMargin+BWIDTH, YMargin+BHEIGHT

	# First fill everything with blue gradient
#	Sx, Sy = max(Width, int(TotalW))+5, max(Height, int(TotalH))+5
#	DefaultBG(Ctx, Sx, Sy)

	if Ysize == 0: # Display text instead of board if no FPGA is found
		Text="No FPGA available in this architecture."
		Ctx.set_source_rgba(1,1,1)  # Write in White
		Ctx.select_font_face("Ubuntu", Cairo.FONT_SLANT_NORMAL, Cairo.FONT_WEIGHT_NORMAL)
		Ctx.set_font_size(FontSize)
		x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
		Ctx.move_to((150+7)-x_off,(150+7)-y_off)
		Ctx.show_text(Text)
		return tw, th
	else:
		FontSize=FontSize*1.3
		# Display architecture name
		DrawText(Ctx, (Xsize+2*FMargin)/2+XMargin, YMargin-Ratio*7, Text=ArchName, Color="Black", Align="Center", Bold=True, FontSize=FontSize, Opacity=1)

	# First draw the board shape --------------------------------------
	Ctx.set_line_width(2)
	Ctx.set_source_rgba(0.9, 0.9, 0.9, 0.3) # White (transparent)
	Ctx.rectangle(XMargin, YMargin, BWIDTH, BHEIGHT)
	Ctx.fill(); # Fill first 
	Ctx.set_source_rgba(0, 0, 0, 0.9) # Black (transparent)
	Ctx.rectangle(XMargin, YMargin, BWIDTH, BHEIGHT)
	Ctx.stroke(); # frame then
	# Then draw the FPGAs ---------------------------------------------
	for Coord, Item in FPGAMatrix.BrowseMatrix():
		(x, y) = Coord
		FPGA = FPGAMatrix.Get(x, y)
		if FPGA!=None:
			xFPGA = FWidth*x  + Space*x + XMargin + FMargin
			yFPGA = FHeight*y + Space*y + YMargin + FMargin
			FPGAParameters=FPGA.Parameters["Common"].copy()
			FPGAParameters.update(FPGA.Parameters["Parent"])
			FPGAParameters.update(FPGA.Parameters["Resources"])
			DrawFPGA(Ctx, FPGAParameters, xFPGA, yFPGA, Ratio=FRatio)
	# Finaly draw the ports -------------------------------------------
	ArrowLen = XMargin-PortBoxSize-PortSpace
	VOffset = 10*Ratio
	if NBPORTS:
		for Port in PortList:
			Ctx.set_line_width(3)
			Ctx.set_source_rgba(0, 0, 0, 0.3) # Black (transparent)
			Ctx.rectangle(PortSpace, VOffset+PortSpace+(PortBoxSize+PortSpace)*PortList.index(Port), PortBoxSize, PortBoxSize)
			Ctx.fill(); # Fill first
			th = Ctx.text_extents(Port.Parameters["Parent"]["Peripheral"])[3]
			DrawText(Ctx, PortSpace+PortBoxSize/2, VOffset+PortSpace+PortBoxSize/2+(PortBoxSize+PortSpace)*PortList.index(Port)+th/2, Text=Port.Parameters["Parent"]["Peripheral"], Color="White", Align="Center", Bold=True, FontSize=12*Ratio, Opacity=0.7)
			
			ArrowHeight = VOffset+PortSpace+(PortBoxSize/2)+(PortBoxSize+PortSpace)*PortList.index(Port)
			ArrowStart  = PortSpace+PortBoxSize
			Ctx.set_source_rgba(0, 0, 0, 0.3) # Black (transparent)
			Ctx.move_to(ArrowStart, ArrowHeight)
			if Port.Parameters["Common"]["Direction"]=="IN": Start=False;End=True;
			elif Port.Parameters["Common"]["Direction"]=="OUT": Start=True;End=False;
			elif Port.Parameters["Common"]["Direction"]=="INOUT": Start=True;End=True;
			else: logging.warning("Wrong value '{0}' for 'Direction' parameters of {1}: unable to stroke arrow.".format())
			DrawArrow(Ctx, ArrowStart+ArrowLen, ArrowHeight, Start=Start, End=End)  # Horizontal
			Ctx.stroke();
			DrawText(Ctx, ArrowStart+ArrowLen/2, ArrowHeight-5*Ratio, Text=Port.Parameters["Common"]["Name"], Color="Black", Align="Center", Bold=False, FontSize=10*Ratio, Opacity=1)

	return TotalW, TotalH

#======================================================================	
def DrawApp(Ctx, AppName, x=20, y=20, Ratio=1):
	"Display information about the application."
	#logging.debug("Display '{0}'".format(AppName))
	FontSize = 16*Ratio

	# Display application name
	Ctx.move_to(x*2, 0)
	Ctx.line_to(x*2, y)
	Ctx.stroke(); 
	W, H = DrawText(Ctx, x/2, 30*Ratio, Text=AppName, Color="Black", Align="Center", Bold=True, FontSize=16*Ratio, Opacity=1)
	return x+W/2, y

#======================================================================	
def DrawAlgo(Ctx, AlgoName, x=20, y=20, Ratio=1):
	"Display information about the algorithm."
	#logging.debug("Display '{0}'".format(AppName))
	FontSize = 16*Ratio

	# Display application name
	Ctx.move_to(x*2, 0)
	Ctx.line_to(x*2, y)
	Ctx.stroke(); 
	W, H = DrawText(Ctx, x/2, 30*Ratio, Text=AlgoName, Color="Black", Align="Center", Bold=True, FontSize=16*Ratio, Opacity=1)
	return x+W/2, y

#======================================================================	
def DrawWelcome(Ctx, Width, Height):#, AdacsysLogo):
	"Display welcome message"
	# Fill everything with blue gradient
	DefaultBG(Ctx, Width, Height)
	Text="YANGO: choose a component to display on the left panel."
#	Ctx.move_to((75+7)-x_off,(Height/4+90)-y_off)
#	ALogo = Pixbuf.new_from_file(AdacsysLogo)
	
#	tw, th = DrawText(Ctx, x=Width/2, y=Height/4+ALogo.get_height()+10, Text=Text, Color="White", Align="Center", Bold=False, FontSize=16, Opacity=1)
	tw, th = DrawText(Ctx, x=Width/2, y=Height/4+10, Text=Text, Color="White", Align="Center", Bold=False, FontSize=16, Opacity=1)
	
#	Gdk.cairo_set_source_pixbuf(Ctx, ALogo, Width/2-60, Height/4)
	Ctx.paint()
	return Width, Height
	
#======================================================================	
def DefaultBG(Ctx, Width, Height):
	"""
	fill everything with blue gradient
	"""
#	return
	Ctx.new_path()
	gradient = Cairo.LinearGradient(0, 0, 0, Height)
	gradient.add_color_stop_rgba(0, 0, 0.5, 0.7, 1) # light blue
	gradient.add_color_stop_rgba(1, 1, 1, 1, 1) # White
	Ctx.set_source(gradient)
	Ctx.rectangle(0,0,Width,Height) # set path
	Ctx.fill()  # fill current path

#======================================================================	
def DrawArrow(Ctx, x, y, Start=True, End=True):
	Cur_x, Cur_y = Ctx.get_current_point()
	#logging.debug("[DrawArrow]Cur_x, Cur_y = {0}, {1}".format(Cur_x, Cur_y))
	#logging.debug("[DrawArrow]x, y = {0}, {1}".format(x, y))
	#logging.debug("[DrawArrow]Start, End = {0}, {1}".format(Start, End))
	ALength  = 10
	ADegrees = 50

	if Start:
		Angle = math.atan2(Cur_y - y, Cur_x - x) + math.pi;
		x1 = Cur_x + ALength * math.cos(Angle - ADegrees);
		y1 = Cur_y + ALength * math.sin(Angle - ADegrees);
		x2 = Cur_x + ALength * math.cos(Angle + ADegrees);
		y2 = Cur_y + ALength * math.sin(Angle + ADegrees);

		Ctx.move_to(Cur_x, Cur_y)
		Ctx.line_to(x1, y1)
		Ctx.move_to(Cur_x, Cur_y)
		Ctx.line_to(x2, y2)

	Ctx.move_to(Cur_x, Cur_y)
	Ctx.line_to(x, y)

	if End:
		Angle = math.atan2(y - Cur_y, x - Cur_x) + math.pi;
		x1 = x + ALength * math.cos(Angle - ADegrees);
		y1 = y + ALength * math.sin(Angle - ADegrees);
		x2 = x + ALength * math.cos(Angle + ADegrees);
		y2 = y + ALength * math.sin(Angle + ADegrees);

		Ctx.move_to(x, y)
		Ctx.line_to(x1, y1)
		Ctx.move_to(x, y)
		Ctx.line_to(x2, y2)
	return True


#======================================================================	
def DrawText(Ctx, x, y, Text=None, Color="Black", Align="Left", Bold=False, FontSize=15, Opacity=1):
	# TODO: Add multiline capabilities
	if not Text: return False

	if Color=="Black": Ctx.set_source_rgba(0, 0, 0, Opacity)
	elif Color=="White":Ctx.set_source_rgba(1, 1, 1, Opacity) 
	elif Color=="Red":Ctx.set_source_rgba(1, 0, 0, Opacity) 
	elif Color=="Green":Ctx.set_source_rgba(0, 1, 0, Opacity) 
	elif Color=="Blue":Ctx.set_source_rgba(0, 0, 1, Opacity)
	elif Color=="Orange":Ctx.set_source_rgba(0.9, 0.9, 0.8, Opacity)
	else: Ctx.set_source_rgba(0, 0, 0, Opacity)

	if Bold: Ctx.select_font_face("Ubuntu", Cairo.FONT_SLANT_NORMAL, Cairo.FONT_WEIGHT_BOLD)
	else: Ctx.select_font_face("Ubuntu", Cairo.FONT_SLANT_NORMAL, Cairo.FONT_WEIGHT_NORMAL)

	Ctx.set_font_size(FontSize)
	x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]

	# Align left
	if Align=="Left": Ctx.move_to(x, y)#-th/2)
	# Align right
	elif Align=="Right": Ctx.move_to(x-tw, y)#-th/2)
	# Align center
	else: Ctx.move_to(x-tw/2, y)#-th/2)

	Ctx.show_text(Text)

	return tw, th

#======================================================================	








