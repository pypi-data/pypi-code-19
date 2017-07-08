import os
import yaml
from fabric.api import env

def _appenv_file():
    base = os.getenv('APPENV_FILE', os.path.join(os.getcwd(), 'deploy'))
    return os.path.join(base, 'appenv.yml')

def set_environment(stage='development'):
    f = open(_appenv_file())
    all_envs = yaml.load(f)
    f.close()
    env.appenv = all_envs[stage]
    env.appenv.update({'stage': stage})
