
import sys
import os

import subprocess as sp
from time import sleep


def hub(port=5001, detached=False, verbose=True, gunicorn=False):
    """
    Launch ezchat hub server
    In new terminal window in detached=True
    """
    name = 'hub'
    filename, msg = create_script(name=name, port=port, verbose=verbose, gunicorn=gunicorn)
    ref = run_script(filename, msg=msg, detached=detached)

    # ref = launch_web_server(name='hub', port=port)
    return ref


def client(port=5002, detached=False, verbose=True):
    """
    Launch ezchat client server
    In new terminal window if detached=True
    """
    name = 'client'
    filename, msg = create_script(name=name, port=port, verbose=verbose)
    ref = run_script(filename, msg=msg, detached=detached)

    # ref = launch_web_server(name='client', port=port)
    return ref


def create_script(name=None, port=5000, verbose=True, gunicorn=False):
    """
    Create run script for chat server or client
    """
    if name not in ['hub', 'client']:
        print('Bad arguments')
        return
    if name == 'client':
        gunicorn = False

    here = os.path.dirname(os.path.realpath(__file__))

    if sys.platform == 'darwin':
        command = "cd {}; export port={}; python {}.py"
        if gunicorn:
            command = "cd {}; export port={}; gunicorn -c gunicorn_conf.py {}:app"
        suffix = 'command'
    elif sys.platform == 'win32':
        command = "cd /d {}; SET port={}; call python {}.py; pause"
        suffix = 'bat'
    elif sys.platform == 'linux':
        command = "cd {}; export port={}; python {}.py"
        if gunicorn:
            command = "cd {}; export port={}; gunicorn -c gunicorn_conf.py {}:app"
        suffix = 'sh'

    filename = os.path.join(here, '{}.{}'.format(name, suffix))
    script = command.format(here, port, name)

    with open(filename, 'w') as f:
        f.write(script)

    msg = 'Open browser to http://localhost:{}'.format(port)
    if verbose:
        print('Script {} created'.format(filename))

    return filename, msg


def run_script(filename, msg=None, detached=False):
    """
    Run script filename
    In new terminal window in detached=True
    """
    here = os.path.dirname(os.path.realpath(__file__))
    name, suffix = os.path.basename(filename).split('.')

    if detached:
        if sys.platform == 'darwin' or sys.platform == 'linux':
            # launch server
            cmd = 'cd {}; chmod +x ./{}.{}; open ./{}.{}'
            cmd = cmd.format(here, name, suffix, name, suffix)
            p = sp.Popen(cmd, stdout=sp.PIPE, shell=True)

            # get process ref: pids
            sleep(0.8)
            cmd = "'python {}.py'".format(name)
            cmd = "ps aux | grep " + cmd + " | grep -v grep | awk '{print $2}'"
            p = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
            res = p.communicate()[0]
            pids = res.decode('utf-8').split('\n')
            pids = [e for e in pids if e != '']
            ref = pids

        elif sys.platform == 'win32':
            # launch server
            cmd = 'cd /d {}; call {}.{}'
            p = sp.Popen([cmd.format(here, name, suffix)],
                         creationflags=sp.CREATE_NEW_CONSOLE)
            # process id is p itself - detached console is windows specific
            ref = p

        print('Web server "ezchat {}" started'.format(name))
        print('To check it is running, look for its terminal window')
        if msg:
            print(msg)
        print('Note: The server will crash upon start if the port is being used')
        return ref

    else:
        if sys.platform == 'darwin' or sys.platform == 'linux':
            # launch server
            cmd = 'bash {}'.format(filename)
            os.system(cmd)

        elif sys.platform == 'win32':
            # launch server
            cmd = '{}'.format(filename)
            os.system(cmd)

        print('Server interrupted: {}'.format(name))
        return None


def kill(ref=None):
    """
    Kill web server identified by its ref (os specific)
    """
    if sys.platform == 'darwin' or sys.platform == 'linux':
        if not isinstance(ref, list):
            print('Wrong reference')
            return

        pids = ref
        print('Killing pids: {}'.format(pids))
        # kill pids
        cmd = 'kill {}'.format(' '.join(pids))
        # os.system(cmd)
        p = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
        print('Server killed')

    elif sys.platform == 'win32':
        if not isinstance(p, sp.Popen):
            print('Wrong reference')
            return

        p = ref
        print('Killing detached console')
        # kill console
        p.kill()
        print('Server killed')
