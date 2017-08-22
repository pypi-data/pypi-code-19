
from mtb.qtWidgets.ColorBand import ColorBand
from random import random
import sys

class Color(object):

    @staticmethod
    def randomColor():
         r = random() * 255
         g = random() * 255
         b = random() * 255

         return (r,g,b)

    @staticmethod
    def gradient(A,B,number=10):

        Ar, Ag, Ab = A
        Br, Bg, Bb = B

        grade = []
        for x in range(0,number):
            percent = x/number
            Cr = Ar + percent * (Br - Ar)
            Cg = Ag + percent * (Bg - Ag)
            Cb = Ab + percent * (Bb - Ab)

            grade.append((Cr,Cg,Cb))

        return grade



if __name__ == "__main__":

    #colorA = Color.randomColor()
    #colorB = Color.randomColor()

    colorA = (0,0,0)
    colorB = (255,255,255)

    gradient = Color.gradient(colorA,colorB,500)

    a = ColorBand.showColors(gradient)

    sys.exit(a.exec_)
