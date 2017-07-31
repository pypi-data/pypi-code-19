import os

from fabric.context_managers import lcd, settings
from fabric.operations import local
from fabric.state import env

from july3 import util
from july3.contrib import mako, git


def bower():
    with settings(warn_only=True):
        if local('type bower').failed:
            local('sudo npm install -g bower')


def django(project_name):
    bower()
    git.checkout(env.project_repository, env.project_path)

    mako.render_template('%s/%s/production.py.mako' % (env.project_path, env.project_name),
                             '%s/%s/production.py' % (env.project_path, env.project_name))

    local('mkdir -p %s/logs' % env.home)
    local('mkdir -p %s/static' % env.home)

    if not os.path.exists('%s/venv' % env.project_path):
        with lcd(env.project_path):
            local('virtualenv venv')

    with lcd(env.project_path):
        local('venv/bin/pip install %s -q -r %s' % (env.get('pip_options', ''), env.pip_filename))
        local('bower install')
        local('venv/bin/python manage.py syncdb --settings=%s.production' % env.project_name)
        local('venv/bin/python manage.py migrate --settings=%s.production' % env.project_name)
        local('venv/bin/python manage.py collectstatic --noinput --settings=%s.production' % env.project_name)

    local('sudo mkdir -p /etc/uwsgi')
    mako.render_builtin_template('uwsgi-app.ini.mako', '/etc/uwsgi/%s.ini' % project_name, sudo=True)
    local('sudo reload uwsgi')

    mako.render_builtin_template('nginx-site.mako', '/etc/nginx/sites-available/%s' % env.project_name, sudo=True)
    util.symlink('/etc/nginx/sites-available/%s' % env.project_name, '/etc/nginx/sites-enabled/%s' % env.project_name)
    local('sudo service nginx reload')


def ensure_mysql(root_password):
    if not package_installed('mysql-server'):
        local("sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password %s'" % root_password, shell='bash')
        local("sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password %s'" % root_password, shell='bash')
        local('sudo apt-get -y install mysql')

    if not local('mysqlshow -uroot -p%s' % root_password).succeeded:
        raise Exception('Cannot connect mysql server with root user')


def uwsgi_emperor():
    local('sudo pip install uwsgi virtualenv -q')

    if not os.path.exists('/etc/init/uwsgi.conf'): # check file updatd
        local('sudo cp %s/files/uwsgi.conf /etc/init/' % os.path.dirname(__file__))
        local('sudo start uwsgi')


def ensure_nodejs():
    with settings(warn_only=True):
        if not local('grep -R node /etc/apt/sources.list /etc/apt/sources.list.d/').succeeded:
            local('sudo add-apt-repository -y ppa:chris-lea/node.js')
            local('sudo apt-get update')
            local('sudo apt-get install -y nodejs')