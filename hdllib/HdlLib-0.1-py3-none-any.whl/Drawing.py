
import math
import logging, os

import cairocffi as cairo

#======================================================================	
def draw_test():

	Width, Height = 400, 250
	output = "./GUI/images/circle.png"

	surf = cairo.ImageSurface(cairo.FORMAT_RGB24,Width,Height)
	Ctx = cairo.Context(surf)

	# fill everything with white
	Ctx.new_path()
	Ctx.set_source_rgb(0.9,0.9,0.9)
	Ctx.rectangle(0,0,Width,Height)
	Ctx.fill()  # fill current path

	# display text in the center
	Ctx.set_source_rgb(0,0,0)  # black
	txt = "Hello, Matthieu !"
	Ctx.select_font_face("Ubuntu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
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
class CairoDrawing:
	#----------------------------------------------------------------------
	def __init__(self, Width=600, Height=400):
		Surface=cairo.ImageSurface(format=cairo.FORMAT_RGB24, width=Width, height=Height)
		self.Ctx = cairo.Context(Surface)
	#----------------------------------------------------------------------
	def ToPNG(self, OutputPath):
		# Save to PNG
		return self.Ctx.get_target().write_to_png(OutputPath)
	#----------------------------------------------------------------------
	def IP(self, Mod, Width=600, Height=400, Ratio=1):
		if(not self.Ctx): 
			logging.error("[Drawing.IP] no context to draw.")
			return False

		IPWidth, IPHeight = 400*Ratio, 400*Ratio 
		x0, y0 = 0,0
		# First fill everything with blue gradient
		Sx, Sy = max(Width, int(IPWidth+x0))+5, max(Height, int(IPHeight+y0))+5
		WhiteBG(self.Ctx, Sx, Sy)
		W, H = DrawIP(self.Ctx, Mod, x=x0, y=y0, Width=Width, Height=Height, Ratio=Ratio, Compact=False)
		if W>Width or H>Height:
			Sx, Sy = max(Width, int(IPWidth+x0))+5, max(Height, int(IPHeight+y0))+5
			Surface=cairo.ImageSurface(format=cairo.FORMAT_RGB24, width=Sx, height=Sy)
			self.Ctx = cairo.Context(Surface)
			WhiteBG(self.Ctx, Sx, Sy)
			W, H = DrawIP(self.Ctx, Mod, x=x0, y=y0, Width=Width, Height=Height, Ratio=Ratio, Compact=False)
		return W, H
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
def DrawIP(Ctx, Mod, x=20, y=20, Width=400, Height=400, Ratio=1, Compact=False, Selected=False):
	"Draw a FPGA in the specified context to x, y location."
	#logging.debug("Display '{0}'".format(Mod.Name))
	PinLength = 20*Ratio
	PinSpace  = 20*Ratio
	FontSize  = 20*Ratio
	CharWidth = 11*Ratio
	Margin    = 20*Ratio
	
	# Get Title width/height
	Title='{0}'.format(Mod.Name)
	TitleFont = 20*Ratio
	LetterWidth = Ctx.text_extents("O")[:4][3]
	while(1):
		Ctx.set_font_size(TitleFont)
		x_off, y_off, tw, th = Ctx.text_extents(Title)[:4]
		if tw+LetterWidth < 200*Ratio: break
		else: TitleFont*=0.95
	
	TitleHeight = th
	PinMargin = TitleHeight	
	
	if Compact is False: 
		######## NEW VERSION ##############
		IOMappings=list(Mod.Ports.values())
		Resets={}#ParamDict["Resets"]
		Clocks={}#ParamDict["Clocks"]
	
		Inputs  = [x.Name for x in [x for x in IOMappings if x.Direction.upper()=="IN"]]
		Outputs = [x.Name for x in [x for x in IOMappings if x.Direction.upper()=="OUT"]]

		# Determine the maximal width of :
		PortsWidth=(max(*[len(i) for i in Inputs])+max(*[len(i) for i in Outputs]))*CharWidth+10
		IPWidth  = max(200*Ratio, tw+PinSpace, PortsWidth) 
		MaxPorts = max(len(Inputs), len(Outputs))
		PortHeight = PinSpace*(MaxPorts)+2*PinMargin+2*FontSize
		IPHeight = max(200*Ratio, PortHeight)
	else: 
		IPWidth  = 200*Ratio
		IPHeight = 200*Ratio
	x0, y0 = (x+Margin+PinLength, y+Margin)

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
			Text=Title, Color="White", Align="Center", Bold=True, 
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
		Ctx.select_font_face("Ubuntu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
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
			# Ctx.set_source_rgba(0.9,0.9,0.8, 1)  # Write in light orange
			Ctx.set_source_rgba(1,1,1, 1)  # Write in white
			x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
			Ctx.move_to((x0+5)-x_off,(y0+2*FontSize+PinSpace*i+PinMargin)-y_off-th/2)
			Ctx.show_text(Text)
		for i in range(0, len(Outputs)): # Outputs
			Ctx.set_source_rgba(0, 0, 0, 1) # Black
			Ctx.move_to(x0+IPWidth, y0+PinSpace*i+PinMargin+2*FontSize)
			DrawArrow(Ctx, x0+IPWidth+PinLength, y0+PinSpace*i+PinMargin+2*FontSize, Start=False, End=True)
			#Ctx.line_to(x0+IPWidth+PinLength, y0+PinSpace*i+PinMargin+2*FontSize)
			Ctx.stroke(); 
			# Display pin names within the frame
			Text=Outputs[i]
			Ctx.set_source_rgba(1,1,1, 1)  # Write in white
			x_off, y_off, tw, th = Ctx.text_extents(Text)[:4]
			Ctx.move_to((x0+IPWidth-tw-5)-x_off,(y0+2*FontSize+PinSpace*i+PinMargin)-y_off-th/2)
			Ctx.show_text(Text)
		# Draw separator between port and NI
		# Ctx.set_source_rgba(0, 0, 0, 1) # Black
		# Ctx.move_to(x0, y0+PinSpace*(MaxPorts)+2*PinMargin+2*FontSize)
		# Ctx.line_to(x0+IPWidth, y0+PinSpace*(MaxPorts)+2*PinMargin+2*FontSize)
		# Draw text = PORTS
		# DrawText(Ctx, x0+IPWidth/2, 
				# y0+PortHeight-2,
				# Text="PORTS", 
				# Align="Center", 
				# Bold=True, 
				# FontSize=15*Ratio, 
				# Opacity=1)
		# Draw text = NETWORK INTERFACE
		# DrawText(Ctx, x0+IPWidth/2, 
				# y0+IPHeight-2,
				# Text="NETWORK INTERFACE", 
				# Align="Center", 
				# Bold=True, 
				# FontSize=15*Ratio, 
				# Opacity=1)
		Ctx.stroke()
		
	return  IPWidth+x0, IPHeight+y0+Margin

#======================================================================	
def WhiteBG(Ctx, Width, Height):
	"""
	fill everything with blue gradient
	"""
	Ctx.new_path()
	Opacity=1
	Ctx.set_source_rgba(1, 1, 1, Opacity) 
	Ctx.rectangle(0,0,Width,Height) # set path
	Ctx.fill()  # fill current path

#======================================================================	
def DefaultBG(Ctx, Width, Height):
	"""
	fill everything with blue gradient
	"""
	Ctx.new_path()
	gradient = cairo.LinearGradient(0, 0, 0, Height)
	gradient.add_color_stop_rgba(0, 0, 0.5, 0.7, 1) # light blue
	gradient.add_color_stop_rgba(1, 1, 1, 1, 1) # White
	Ctx.set_source(gradient)
	Ctx.rectangle(0,0,Width,Height) # set path
	Ctx.fill()  # fill current path

#======================================================================	
def DrawArrow(Ctx, x, y, Start=True, End=True):
	Cur_x, Cur_y = Ctx.get_current_point()
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

	if Bold: Ctx.select_font_face("Ubuntu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
	else: Ctx.select_font_face("Ubuntu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

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








