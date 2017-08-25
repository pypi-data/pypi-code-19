from jpype import *
from ._pyconrad import PyConrad

def makeSimpleVector(vec):
    return JClass('edu.stanford.rsl.conrad.numerics.SimpleVector')(JArray(JDouble)(vec))

def makePointND(vec):
    return JClass('edu.stanford.rsl.conrad.geometry.shapes.simple.PointND')(JArray(JDouble)(vec))
