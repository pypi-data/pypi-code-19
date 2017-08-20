#!/usr/bin/env python
import subprocess
import sys
import os
import ast

MY_LOC = os.path.dirname(os.path.abspath(__file__))

def build_storage():
    content = []
    with open(MY_LOC + '/storage.py', 'r') as fh:
        for line in fh:
            listobj = eval(line)
            content.append(listobj)
    return content

def shell_source(script):
    """Sometime you want to emulate the action of "source" in bash,
    settings some environment variables. Here is a way to do it."""
    import subprocess, os
    pipe = subprocess.Popen(". %s; env" % script, stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    env = dict((line.split("=", 1) for line in output.split('\x00')))
    os.environ.update(env)

def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()

def print_subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)

class ExceptionTemplate(Exception):
    def __call__(self, *args):
        return self.__class__(*(self.args + args))

class AlreadyExists(ExceptionTemplate): pass

''' If no arguements, display help and quit '''
try:
    first_arg = sys.argv[1]
except Exception:
    print('---')
    print('DevBox by Dion Misic // 2017')
    print('---')
    print('devbox create <project_name> - Create project at current path')
    print('devbox projects - View projects')
    print('devbox open <project_name> - Open project')
    print('---')
    quit()

''' If arguements received, react appropriately '''
try:
    if first_arg == "create":
        # Check for arguements
        try:
            proj_name = sys.argv[2]
            content = build_storage()
            exists = AlreadyExists('Already exists! Try again!')
            for project in content:
                if project['Project'] == proj_name:
                    raise exists
        except AlreadyExists as e:
            print(e)
            print('USAGE: devbox create <project_name>')
            quit()
        location = os.getcwd()

        # Add to devbox list
        print("Creating devbox(" + proj_name +") at: " + location)
        devbox = {'Project': proj_name, 'Location': location}
        representation = repr(devbox)

        if os.stat(MY_LOC + "/storage.py").st_size == 0:
             f = open(MY_LOC + '/storage.py', 'a' )
             f.write(representation)
             f.close()
        else:
            f = open(MY_LOC + '/storage.py', 'a' )
            f.write('\n' + representation)
            f.close()

        # Create directory
        subprocess_cmd('cd; cd ' + location + '; mkdir ' + proj_name +
                    '; cd ' + proj_name + '; pip3 install virtualenv; virtualenv ' + proj_name + '-devbox; cp ' +
                    MY_LOC + '/cdme ' + location + '/' + proj_name)


    if first_arg == "projects":
        content = build_storage()
        counter = 1
        for project in content:
            print(str(counter) + ". " + project['Project'] + " (" + project['Location'] + ")")
            counter += 1

    if first_arg == "reset":
        scpt = '''tell application "Terminal"
                    close rest of (get windows)
                end tell'''

        p = Popen(['osascript', '-'], universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(scpt)

    if first_arg == "open":
        try:
            proj_name = sys.argv[2]
        except:
            print('USAGE: devbox open <project_name>')
            quit()

        redirect = ""
        redirect_name = ""
        content = build_storage()
        for project in content:
            if project['Project'].lower() == proj_name.lower():
                redirect = project['Location']
                redirect_name = project['Project']
        if redirect == "":
            print('Project not found!')
            quit()

        loc = redirect + '/' + redirect_name

        print('---')
        print('DevBox is opening your project. Might take a second!')
        print('---')


        from subprocess import Popen, PIPE

        fileloc = loc + '/cdme'
        execute_me = 'python2.7 ' + MY_LOC + '/terminal.py ' + fileloc + ' ' + loc + ' ' + proj_name
        print(execute_me)

        subprocess_cmd(execute_me)

        scpt = '''tell application "Terminal"
                    close rest of (get windows)
                end tell'''

        p = Popen(['osascript', '-'], universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(scpt)


except Exception as e:
    print('Came in here')
    print(e)
