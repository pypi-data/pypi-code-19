#!/usr/bin/env python3

import os
import sys
from subprocess import call
from os.path import expanduser

ALIASES = {
    # Django
    'c'  : 'collectstatic',
    'r'  : 'runserver',
    'sp' : 'startproject',
    'sa' : 'startapp',
    't'  : 'test',

    # Shell
    's'  : 'shell',
    'sh' : 'shell',

    # Auth
    'csu': 'createsuperuser',
    'cpw': 'changepassword',

    # Migrations
    'm'  : 'migrate',
    'mg' : 'migrate',
    'mkm': 'makemigrations'
}


def run(in_arguments):
    """
    Run the given command.

    Loads extra commands from file.

    Parameters:
    :param arguments: A list of strings describing arguments to the command.
    """
    
    flags = []
    command = None
    arguments = []

    for arg in in_arguments:
        if command is None:
            if arg[0] == '-':  # e.g. -Wall
                flags.append(arg)
            else:
                command = arg
        else:
            arguments.append(arg)
    
    if command is None:
        msg = 'django-shts3: No command was supplied, please specify one.'
        
        if not flags == []:
            msg += ' (all arguments before first command starting with `-` are threated as python flags like `-Wall`)'
        sys.exit(msg)

    script_path = os.getcwd()
    while not os.path.exists(os.path.join(script_path, 'manage.py')):
        base_dir = os.path.dirname(script_path)
        if base_dir != script_path:  # we reached `/` directory
            script_path = base_dir
        else:
            sys.exit('django-shts3: No \'manage.py\' script found in this directory or its parents.')
    
    config_file_path = os.path.join(expanduser("~"), ".django_shts3")
    with open(config_file_path, "r") as conifg_file:
        for x in conifg_file:
            parsed = x.split(" @@@ ")
            if not len(parsed) == 2:
                sys.exit("django-shts3: can't parse config file .django_shts3 (in your home dir)")
            alias = parsed[0]
            actual = parsed[1]
            ALIASES[alias] = actual

    if command in ALIASES:
        command = ALIASES[command]
    
    shell_cmd = '%(python)s %(flags)s %(script_path)s %(command)s %(arguments)s' % {
        'python': sys.executable,
        'flags': ' '.join(flags),
        'script_path': os.path.join(script_path, 'manage.py'),
        'command': command,
        'arguments': ' '.join(arguments)
    }
    
    return call(shell_cmd, shell=True)

def main():
    """Entry-point function."""
    sys.exit(run(sys.argv[1:]))

if __name__ == '__main__':
    main()
