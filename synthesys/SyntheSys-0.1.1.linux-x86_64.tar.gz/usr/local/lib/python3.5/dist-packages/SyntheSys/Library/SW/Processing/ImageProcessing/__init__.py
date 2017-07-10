#! /usr/bin/python3

"""
Image processing functions
"""

__all__=["AxisXYZ", "CIE_b", "DistanceRGB", "Green", "RegionMean", "Blue", "CIE_L", "DistanceRMS", "CIE_a", "DistanceGFC", "DistanceWRMS", "Red"]


#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import AxisXYZ
AxisXYZ = AxisXYZ.__BASICBLOCK__AxisXYZ()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import CIE_L
CIE_L = CIE_L.__BASICBLOCK__CIE_L()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import CIE_a
CIE_a = CIE_a.__BASICBLOCK__CIE_a()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import CIE_b
CIE_b = CIE_b.__BASICBLOCK__CIE_b()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import Red
Red = Red.__BASICBLOCK__Red()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import Blue
Blue = Blue.__BASICBLOCK__Blue()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import Green
Green = Green.__BASICBLOCK__Green()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import DistanceRGB
DistanceRGB = DistanceRGB.__BASICBLOCK__DistanceRGB()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import DistanceRMS
DistanceRMS = DistanceRMS.__BASICBLOCK__DistanceRMS()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import DistanceWRMS
DistanceWRMS = DistanceWRMS.__BASICBLOCK__DistanceWRMS()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import DistanceGFC
DistanceGFC = DistanceGFC.__BASICBLOCK__DistanceGFC()

#----------------------------------------------
from SyntheSys.Library.SW.Processing.ImageProcessing import RegionMean
RegionMean = RegionMean.__BASICBLOCK__RegionMean()












