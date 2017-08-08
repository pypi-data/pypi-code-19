import json
import re
import subprocess
import shutil
import os
import pip
import importlib
import sys
from subprocess import Popen, PIPE
from .utils import *
from .functions import *

# pyenv check
check_pyenv_installed()

# argv check
project_name = parse_project_name()
env_name = '%s-env' % project_name

# pyenv version list
python_version = select_python_version()

# Make project folder
if os.path.exists(project_name):
    shutil.rmtree(project_name)
# subprocess.call('pyenv uninstall -f %s' % env_name, shell=True)
os.mkdir(project_name)
os.chdir(project_name)

# pyenv make virtualenv
subprocess.call('pyenv virtualenv %s %s' % (
    python_version,
    env_name,
), shell=True)

# pyenv local
subprocess.call('pyenv local %s' % (
    env_name,
), shell=True)

# pyenv path
pyenv_path = get_pyenv_path(python_version, env_name)
pyenv = Pyenv(pyenv_path)

# install django, startproject
pyenv.call('pip install django')
pyenv.call('django-admin startproject config')

# django application folder rename
os.rename('config', 'django_app')
os.chdir('django_app/config')

# settings.py
secret_list = [
    {
        'regex': r'SECRET_KEY = \'(?P<secret_key>.*?)\'.*?\n',
        'key': 'secret_key',
        'group': 'secret_key',
        'preserve': False
    }
]
secret_dict = {}
replacements = {
    'Django settings for config project.': 'Django settings for %s project.' % project_name,
}
lines = []
ori = open('settings.py').read()
out = open('settings.py', 'w')
for secret in secret_list:
    value = re.search(secret['regex'], ori).group(secret['group'])
    secret_dict[secret['key']] = value
    if value and not secret.get('preserve'):
        ori = re.sub(secret['regex'], '', ori)

for src, target in replacements.items():
    ori = re.sub(src, target, ori)
out.write(ori)
out.close()
print(secret_dict)

# create config directories
os.chdir('../../')
os.mkdir('.config')
os.mkdir('.config_secret')
os.mkdir('.requirements')

# secret config to json file
secret_config = {
    'django': {
        'secret_key': secret_dict['secret_key'],
    }
}
open('.config_secret/settings_common.json', 'w').write(json.dumps(secret_config, indent=4, sort_keys=True))

# requirements
pyenv.call('pip freeze > .requirements/debug.txt')
