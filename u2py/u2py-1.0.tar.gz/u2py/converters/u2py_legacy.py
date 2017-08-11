from PyQt4 import uic

def convert(uifile,outputfile=None):
    if outputfile is None:
        uifilename = uifile[0:len(uifile)-3]
        outputfile = uifilename + '_ui.py'
    print('Converting ' + uifile + '\t->\t' + outputfile)

    fp = open(outputfile,'w')
    uic.compileUi(uifile,fp)
    fp.close()
    print('Saved as ' + outputfile)