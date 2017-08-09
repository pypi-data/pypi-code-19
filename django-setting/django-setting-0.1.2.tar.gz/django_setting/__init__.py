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

# Paths
CWD = os.getcwd()
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_FILE_DIR = os.path.join(PACKAGE_DIR, 'files')
print(PACKAGE_DIR)
print(PACKAGE_FILE_DIR)

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
pyenv.call('pip install django django_extensions ipython')
pyenv.call('django-admin startproject config')

# django application folder rename
os.rename('config', 'django_app')

# move to django_app folder and make django directories
os.chdir('django_app')
os.mkdir('templates')
os.mkdir('static')

# startapp member
pyenv.call('python manage.py startapp member')
with open('member/models.py', 'w') as f:
    f.write('''from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
''')
    f.close()

# settings.py
os.chdir('config')
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
    # import
    r'import os': r'import os\nimport json',
    # project name
    'Django settings for config project.': 'Django settings for %s project.' % project_name,

    # root, template, static paths
    r'\n(BASE_DIR.*?\n)': r'''
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# .config folder and files
CONFIG_SECRET_DIR = os.path.join(ROOT_DIR, '.config_secret')
CONFIG_SECRET_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, 'settings_common.json')
CONFIG_SECRET_DEBUG_FILE = os.path.join(CONFIG_SECRET_DIR, 'settings_debug.json')
CONFIG_SECRET_DEPLOY_FILE = os.path.join(CONFIG_SECRET_DIR, 'settings_deploy.json')

config_secret_common = json.loads(open(CONFIG_SECRET_COMMON_FILE).read())

SECRET_KEY = config_secret_common['django']['secret_key']

AUTH_USER_MODEL = 'member.User'

STATICFILES_DIRS = [
    STATIC_DIR,
]

''',

    # template dirs
    re.compile(r'(?P<before>\nTEMPLATES = .*?\n)(?P<indent>\s+)(?P<key>\'DIRS\': )(?P<value>\[\]),', re.DOTALL):
        r'\g<before>\g<indent>\g<key>[\n\g<indent>    TEMPLATE_DIR,\n\g<indent>],',

    # INSTALLED_APPS
    re.compile(r'(\nINSTALLED_APPS = .*?)(\n])', re.DOTALL):
        r"""\g<1>
    'member',
]
""",
}
lines = []
ori = open('settings.py').read()
os.remove('settings.py')
os.mkdir('settings')
open('settings/__init__.py', 'w').write('''import os

SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
if not SETTINGS_MODULE or SETTINGS_MODULE == 'config.settings':
    from .debug import *
''')
out = open('settings/base.py', 'w')
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

with open('settings/debug.py', 'w') as settings_debug:
    settings_debug.write('''from .base import *
# config_secret_debug = json.loads(open(CONFIG_SECRET_DEBUG_FILE).read())

# INSTALLED_APPS
INSTALLED_APPS.append('django_extensions')

# Static URLs
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT_DIR, '.static_root')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(ROOT_DIR, '.media')
''')

# create config directories
os.chdir('../../')
os.mkdir('.config')
os.mkdir('.config_secret')
os.mkdir('.requirements')
os.mkdir('.media')
gitignore = open(os.path.join(PACKAGE_FILE_DIR, 'gitignore')).read()
with open('.gitignore', 'w') as f:
    f.write(gitignore)

# secret config to json file
secret_config = {
    'django': {
        'secret_key': secret_dict['secret_key'],
    }
}
open('.config_secret/settings_common.json', 'w').write(json.dumps(secret_config, indent=4, sort_keys=True))

# requirements
pyenv.call('pip freeze > .requirements/debug.txt')

# move to django_app directory
os.chdir('django_app')

# makemigrations and migrate
pyenv.call('python manage.py makemigrations')
pyenv.call('python manage.py migrate')

os.chdir('..')
subprocess.call('git init', shell=True)
subprocess.call('git add -A', shell=True)
subprocess.call('git commit -m \'First commit\'', shell=True)