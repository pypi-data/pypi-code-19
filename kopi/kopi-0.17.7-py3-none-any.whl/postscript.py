
__all__=["PS_ShowMeAllAsciiCharWidth"]

def PS_ShowMeAllAsciiCharWidth(Font="Helvetica", FontSize=10):#{{{
	OriginX = 100
	OriginY= 600
	x = OriginX
	y = OriginY
	Indent = 40
	Spacing = 1.6
	OutputString=PS_selecfont(Font, FontSize)

	for n in range(32,64):
		OutputString+=PS_moveto(x, y)
		S="\\%o"%n
		OutputString += PS_show(S) +\
				PS_moveto(x + Indent, y) +\
				"(" + S + ")stringwidth pop 10 string cvs show\n"
		y = y-Spacing*FontSize

	x=x+4*Indent
	y=OriginY
	for n in range(64,96):
		OutputString+=PS_moveto(x, y)
		S="\\%o"%n
		OutputString += PS_show(S) +\
				PS_moveto(x + Indent, y) +\
				"(" + S + ")stringwidth pop 10 string cvs show\n"
		y = y-Spacing*FontSize

	x=x+4*Indent
	y=OriginY
	for n in range(96,127):
		OutputString+=PS_moveto(x, y)
		S="\\%o"%n
		OutputString += PS_show(S) +\
				PS_moveto(x + Indent, y) +\
				"(" + S + ")stringwidth pop 10 string cvs show\n"
		y = y-Spacing*FontSize

	OutputString+="clear\n"
	for n in range(95):
		S="\\%o"%(126-n)
		OutputString+= "(" + S + ")stringwidth pop\n"
	OutputString+="stack\n"
	return OutputString #}}}
