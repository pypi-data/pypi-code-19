import sys

try:
    shell = sys.stdout.shell
except:
    shell = sys.stdout

def black(text='', end='\n'):
    colorprint(text, end, 'SYNC')

def red(text='', end='\n'):
    colorprint(text, end, 'COMMENT')

def green(text='', end='\n'):
    colorprint(text, end, 'STRING')

def blue(text='', end='\n'):
    colorprint(text, end, 'stdout')

def purple(text='', end='\n'):
    colorprint(text, end, 'BUILTIN')

def orange(text='', end='\n'):
    colorprint(text, end, 'KEYWORD')

def colorprint(text='', end='\n', flag=''):
    try:
        shell.write(str(text)+end, flag)
    except TypeError:
        shell.write(str(text)+end)


def trace(text=''):
    black('TRACE: ' + text)

def debug(text=''):
    purple('DEBUG: ' + text)

def info(text=''):
    green('INFO: ' + text)

def warning(text=''):
    shell.write('WARNING: ' + text + '\n', 'stderr')

def error(text='', exeption=None):
    shell.write('ERROR: '+text+'\n', 'ERROR')
    if exception is not None:
        shell.write(str(exception), 'ERROR')

