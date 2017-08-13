# -*- coding: utf-8 -*-
from distutils.core import setup
setup(
    name='teamroles',
    packages=['teamroles', 'teamroles.models', 'teamroles.middleware', 'teamroles.migrations'],
    version='0.1.8',
    description='Implementation of User-Role-Team-Permissions network with Django web framework',
    author='Mevlana Ayas',
    author_email='mevlanaayas@gmail.com',
    license='MIT',
    url='https://github.com/mevlanaayas/django-teams.git',
    download_url='https://github.com/mevlanaayas/django-teams/tarball/0.1.8',
    keywords=['django', 'django-teams', 'django teams', 'role permissions', 'roles'],
    classifiers=[],
)
