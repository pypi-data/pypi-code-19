# -*- coding:utf-8 -*-
import sys
import argparse
import os
import git
from cmd.command import Application


def _generate_templates(name):
    os.mkdir(name)
    os.chdir(name)

    pkg_pth = os.path.split(os.path.realpath(__file__))[0]
    app_pth = os.path.join(pkg_pth, 'templates', 'app')
    models = os.path.join(app_pth, 'models.tmpl')
    views = os.path.join(app_pth, 'views.tmpl')
    including = os.path.join(app_pth, 'including.tmpl')

    with open('models.py', 'wb') as f:
        f.write(open(models, 'rb').read())

    with open('views.py', 'wb') as f:
        f.write(open(views, 'rb').read())

    with open('INCLUDING', 'wb') as f:
        f.write(open(including, 'rb').read())

    with open('__init__.py', 'wb') as f:
        f.write('')


def execute(argv=None, settings=None):
    if argv is None:
        argv = sys.argv

    if len(sys.argv) == 1:
        sys.argv.append('--help')

    parser = argparse.ArgumentParser()
    parser.add_argument('operator', choices=('bind', 'generate', 'upload'))
    parser.add_argument('--name', '-n', help='name for your app')

    args = parser.parse_args()
    operator = args.operator
    if operator == 'bind':
        app = Application()
        app.bind()

    elif operator == 'generate':
        name = args.name
        if name is None:
            print '需要指定名称 [--name or -n]'
            return
        _generate_templates(name)

    elif operator == 'upload':
        app = Application()
        app.upload()


if __name__ == '__main__':
    execute()
