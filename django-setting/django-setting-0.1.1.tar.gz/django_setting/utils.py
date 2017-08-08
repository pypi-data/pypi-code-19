import subprocess
from subprocess import Popen, PIPE


def get_subprocess_output(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    return out.decode('utf-8')


def get_latest_pyenv_python_version():
    # pyenv install last version
    p = Popen(['pyenv', 'install', '--list'], stdout=PIPE)
    out, err = p.communicate()
    out = out.decode('utf-8')
    version_list = out.split('\n')
    version_list = [x.strip() for x in version_list if x.strip().startswith('3') and 'dev' not in x]
    last_version = version_list.pop()
    return last_version


class Pyenv:
    def __init__(self, pyenv_path):
        self.pyenv_path = pyenv_path

    def call(self, cmd):
        subprocess.call('%s/bin/%s' % (
            self.pyenv_path,
            cmd
        ), shell=True)

