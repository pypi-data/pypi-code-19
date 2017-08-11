import pip
import sys
# from PyQt5 import uic
arg = sys.argv

# def checkforpyqt():
#     try:
#         global x
#         from PyQt5 import uic as x
#     except ImportError as e:
#         try:
#             global x
#             from PyQt4 import uic as x
#         except ImportError as e2:
#             print('\nError... PyQt4 or greater required')
#             print('Try python -m pip install PyQt4\n')
#             exit(-1)

# def u2py(uifile,outputfile=None):
#     if outputfile is None:
#         uifilename = uifile[0:len(uifile)-3]
#         outputfile = uifilename + '_ui.py'
#     print('Converting ' + uifile + '\t->\t' + outputfile)
#
#     fp = open(outputfile,'w')
#     uic.compileUi(uifile,fp)
#     fp.close()
#     print('Saved as ' + outputfile)



def show_usage():
    print('\nu2py is a utility built by using python\n')
    print('Usage:\n\tpython u2py <inputfile> [options]\n')
    print('Options:')
    print('\t-h, --help\t\t\tShow Help')
    print('\toutput=<path>\t\t\tOutput File\n')

def getConverterFunction():
    try:
        import PyQt5
        print('Found \'Pyqt5\'. Using \'PyQt5\' for converting ui files to py files.')
        from u2py.converters.u2py import convert
        return (convert,'found')
    except ImportError as e:
        print(e)
        print('Checking for PyQt4')
        try:
            import PyQt4
            print('Fallback successfull: Found \'Pyqt4\'. Using \'PyQt4\' for converting ui files to py files.')
            from u2py.converters.u2py_legacy import convert
            return (convert,'PyQt5')
        except ImportError as e2:
            print(e2)
            return (None,'both')

def config(flag):
    if sys.platform == 'win32':
        print(
            'You can add an option in Send To Sub Menu to directly convert ui files to py files in the same directory.')
        print(
            'CAUTION: If you uninstall u2py and you have enabled Send To option, you need to manually remove co.cmd file from your disk')
        print('Do you want to create a Send To Option?(Windows only)(y/n)')
        ch = input()
        if ch in ['y', 'Y']:
            createSendToOption()
    if flag == 'both':
        print('Select which PyQt version to download:')
        print('1.PyQt5(recommended)')
        print('2.PyQt4')
        print('3.Exit')
        ch = input()
        if ch == '1':
            install('PyQt5')
        elif ch == '2':
            install('PyQt4')
        elif ch == '3':
            return
        else:
            print('Wrong choice')
            config(flag)

def install(pacakage):
    pip.main(['install',pacakage])

def main(args=None):
    u2py,flag = getConverterFunction()
    if u2py is None:
        return
    if flag == 'both':
        print('PyQt version not found.')
        print('Opening configuration page')
        config(flag)
    if len(arg) == 1:
        print('\nError: No input file\n')
        print('\nTry --help\n')
        return
    elif '--help' in arg or '-h' in arg:
        show_usage()
        return
    elif 'config' in arg :
        config(flag)
        return
    elif not arg[1].endswith('.py'):
        print('Please enter a valid file name')
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
        import pkg_resources,os
        data = pkg_resources.resource_string('u2py','config/co.cmd')
        sendTofilelocation = os.environ['USERPROFILE'] + '\\AppData\Roaming\\Microsoft\\Windows\\SendTo\\Convert to py.cmd'
        f = open(sendTofilelocation,'wb')
        f.write(data)
        f.close()
        print('Successfully created a Send To shortcut')
    else:
        print('Error: This option only available in windows')

if __name__ == '__main__':
    main()