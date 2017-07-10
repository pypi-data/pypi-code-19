import sys

shell = sys.stdout.shell

def black(text='', end='\n'):
    shell.write(str(text)+end, 'SYNC')

def red(text='', end='\n'):
    shell.write(str(text)+end, 'COMMENT')

def green(text='', end='\n'):
    shell.write(str(text)+end, 'STRING')

def blue(text='', end='\n'):
    shell.write(str(text)+end, 'stdout')

def purple(text='', end='\n'):
    shell.write(str(text)+end, 'BUILTIN')

def orange(text='', end='\n'):
    shell.write(str(text)+end, 'KEYWORD')

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

