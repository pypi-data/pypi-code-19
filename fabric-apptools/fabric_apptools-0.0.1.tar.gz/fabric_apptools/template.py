import os
import tempfile
import jinja2
from fabric.api import env
from fabric_apptools.appenv import set_environment

def _template_path():
    return os.getenv('APP_TEMPLATE_PATH', os.path.join(os.getcwd(), 'deploy', 'templates'))

def _jinja2_env():
    return jinja2.Environment(loader=jinja2.FileSystemLoader(_template_path()))

def build_template(name, path=None, params=None, stage='development'):
    j2env = _jinja2_env()
    template = j2env.get_template(name)
    if not path:
        path = os.path.join(tempfile.mkdtemp(), os.path.basename(name))
    if not params:
        if 'appenv' not in env:
            set_environment(stage)
        params = env.appenv
    f = open(path, 'w')
    f.write(template.render(params))
    f.close()
    return path
