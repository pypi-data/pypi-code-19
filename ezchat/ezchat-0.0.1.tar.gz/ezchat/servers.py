
import sys
import os

import subprocess as sp
from time import sleep


def hub(port=5001):
    """
    Launch ezchat hub server in new terminal window
    """
    ref = launch_web_server(name='hub', port=port)
    return ref


def client(port=5002):
    """
    Launch ezchat client server in new terminal window
    """
    ref = launch_web_server(name='client', port=port)
    return ref


def launch_web_server(name=None, port=5000):
    """
    Launch web server for chat server of client in new terminal window
    """
    if name not in ['hub', 'client']:
        print('Bad arguments')
        return

    here = os.path.dirname(os.path.realpath(__file__))

    if sys.platform == 'darwin':
        command = "cd {}; export port={}; python {}.py"
        suffix = 'command'
    elif sys.platform == 'win32':
        command = "cd /d {}; SET port={}; call python {}.py; pause"
        suffix = 'bat'
    elif sys.platform == 'linux':
        command = "cd {}; export port={}; python {}.py"
        suffix = 'sh'

    with open(os.path.join(here, '{}.{}'.format(name, suffix)), 'w') as f:
        f.write(command.format(here, port, name))

    if sys.platform == 'darwin' or sys.platform == 'linux':
        # launch server
        cmd = 'cd {}; chmod +x ./{}.{}; open ./{}.{}'
        cmd = cmd.format(here, name, suffix, name, suffix)
        # os.system(cmd)
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

    print('Web server "chat {}" started'.format(name))
    print('To check it is running, look for its terminal window')
    print('And open browser to http://localhost:{}'.format(port))
    print('Note: The server will crash upon start if the port is being used')
    return ref


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
