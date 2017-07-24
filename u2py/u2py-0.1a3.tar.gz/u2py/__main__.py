import sys
arg = sys.argv

def checkforpyqt():
    try:
        global x
        from PyQt5 import uic as x
    except ImportError as e:
        try:
            global x
            from PyQt4 import uic as x
        except ImportError as e2:
            print('\nError... PyQt4 or greater required')
            print('Try python -m pip install PyQt4\n')
            exit(-1)

def u2py(uifile,outputfile=None):
    if outputfile is None:
        uifilename = uifile[0:len(uifile)-3]
        outputfile = uifilename + '_ui.py'
    print('Converting ' + uifile + '\t->\t' + outputfile)

    fp = open(outputfile,'w')
    x.compileUi(uifile,fp)
    fp.close()
    print('Saved as ' + outputfile)



def show_usage():
    print('\nu2py is a utility built by using python\n')
    print('Usage:\n\tpython u2py <inputfile> [options]\n')
    print('Options:')
    print('\t-h, --help\t\t\tShow Help')
    print('\toutput=<path>\t\t\tOutput File\n')

def main(args=None):
    checkforpyqt()
    if len(arg) == 1:
        print('\nError: No input file\n')
        print('\nTry --help\n')
        return
    elif '--help' in arg or '-h' in arg:
        show_usage()
        return
    else:
        if 'output=' in arg[1]:
            print('\nError: No input file\n')
            return
        else:
            uifile = arg[1]
            outfile = None
            if len(arg) == 3 :
                if 'output=' in arg[2] :
                    if len(arg[2]) > 7:
                        outfile = arg[2][7:]
                    else:
                        print('\nError: No output file\n')
                        return
                else:
                    outfile = arg[2]

            u2py(uifile,outfile)


def createSendToOption():
    if sys.platform == 'win32':
        import os
        sendTofilelocation = os.environ['USERPROFILE'] + '\\AppData\Roaming\\Microsoft\\Windows\\SendTo\\Convert to py'
        newfile = open(sendTofilelocation,'w')
        myfile = open('co.cmd','r')
        inp = myfile.read()
        newfile.write(inp)
        newfile.close()
        myfile.close()


if __name__ == '__main__':
    main()