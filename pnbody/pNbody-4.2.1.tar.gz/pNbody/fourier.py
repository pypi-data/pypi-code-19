from numpy import *
''' 
 @package   pNbody
 @file      fourier.py
 @brief     Fourier Transform
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''


from numpy import fft


####################################  
def tofrec(fmin,fmax,n,i):
####################################
  nn = float(n)
  if i<=n/2+1:
    return (i/nn+0.5)*(fmax-fmin) + fmin
  else:
    return (i/nn-0.5)*(fmax-fmin) + fmin 


####################################
def fourier(x,y):
####################################
  '''
  
  Fct = Sum_(m=1,n) amp_m cos( 2.pi f_m phi + phi_m )
      = Sum_(m=1,n) amp_m cos(        m phi + phi_m )
  
  m = 2.pi f_m
  
  '''
  
  dx = (x.max()-x.min())/(len(x)-1)
  fmin = -1./(2.*dx)
  fmax = -fmin
  
  #f = fromfunction(lambda ii:tofrec(fmin,fmax,len(x),ii) ,(len(x),))  
  f = array([],float)
  for i in range(len(x)):
    f = concatenate((f,array([tofrec(fmin,fmax,len(x),i)])))


  ## FFT ##  
  ffft = fft.fft(y)
  
  amp = sqrt(ffft.real**2 + ffft.imag**2)	# amplitude du signal d'entree
  phi = arctan2(ffft.imag,ffft.real)		# phase a p/2 pres
  phi = fmod(phi+2*pi,2.*pi)			# de 0 a 2*pi (ok avec phase positive)
  
  
  amp = 2.* amp / len(x)			# doubler ok, /len(x) ???		
  
  f = f[0:len(x)/2]				# on sort que les frequences positives
  amp = amp[0:len(x)/2]
  phi = phi[0:len(x)/2]
  
  amp[0] = amp[0]/2.
  
  return f,amp, phi     

