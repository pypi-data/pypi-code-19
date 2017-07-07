from distutils.core import setup
from shutil import copyfile
from os import chmod

setup(
    name='smeagol',
    version='0.1.2',
    author='Josh Kaplan',
    author_email='contact@joshkaplan.org',
    url='https://github.com/josh-kaplan/smeagol',
    license='MIT',
    description='A Python Wiki',
    long_description=open('README.md').read(),
    keywords='wiki',
    packages=['smeagol', 'smeagol.static', 'smeagol.templates'],
    package_data={'smeagol': ['static/*', 'templates/*', 'templates/includes/*']},
    scripts=['bin/smeagol'],
    install_requires=['Flask', 'Markdown', 'py-gfm'],
    python_requires='==2.7'
)
