


from pylab import *

xL = range(40)
yL = [2. + 0.2*x +0.02*x**2  for x in xL]

plot(xL, yL, label='y = 2 + 0.2x + 0.02x^2', linewidth=3)

legend(loc='upper left')
grid(True)
title( 'Digitizing Sample Plot\nVerify Results with Excel Trendline' )
xlabel( 'X Value' )
ylabel( 'Y Value' )
savefig('sample_poly.png', dpi=120)

show()
