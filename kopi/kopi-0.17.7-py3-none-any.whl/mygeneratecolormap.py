#!python3
print("Generate Jet Color Map data (256 colors, Linear, Normalized values)")
Max = 255
Half = 128
Min = 0
for x in range(256):
	R = (x-Half)/(Max - Half) if x>Half else 0
	G = x/(Half-Min) if x<Half else (1-(x-Half)/(Max-Half))
	B = 1 - x/(Half-Min) if x<Half else 0
	print("[",R,", ",G,", ",B,"],")
