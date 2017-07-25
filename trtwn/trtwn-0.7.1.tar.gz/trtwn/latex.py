import trtwn.fs
import trtwn.matplotlib
import os

def inputStr(path):
    return '\\input{%s}\n' % path

def pythontex(filename, outputDir):
    filename = trtwn.fs.purename(filename)
    filepath = os.path.join(outputDir, filename + ".pgf")

    trtwn.matplotlib.savePgfAndPdf(filepath)

    print(inputStr(filepath))
