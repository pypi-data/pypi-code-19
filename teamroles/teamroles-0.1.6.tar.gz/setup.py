# -*- coding: utf-8 -*-
from distutils.core import setup
setup(
    name='teamroles',
    packages=['teamroles', 'teamroles.models', 'teamroles.middleware', 'teamroles.migrations'],  # this must be the same as the name above
    version='0.1.6',
    description='Version that includes django models, mixins and middleware',
    author='Mevlana Ayas',
    author_email='mevlanaayas@gmail.com',
    url='https://github.com/mevlanaayas/django-teams.git',  # Github URL
    download_url='https://github.com/mevlanaayas/django-teams/tarball/0.1.6',
    keywords=['django', 'django-teams', 'django teams', 'role permissions', 'roles'],  # Descriptive keywords
    classifiers=[],
)
