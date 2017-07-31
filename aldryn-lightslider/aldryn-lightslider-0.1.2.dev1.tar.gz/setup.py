import os
from setuptools import find_packages, setup
import aldryn_lightslider

version = aldryn_lightslider.__version__
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='aldryn-lightslider',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=(
        'django-filer',
        'django-cms>=3.0',
        'djangocms-admin-style',
        'cmsplugin-filer',
    ),
    # install_requires=[i.strip() for i in open(os.path.join(here,"requirements.txt")).readlines()],
    license='GNU License', 
    description='LightSlider aldryn addon and djangocms plugin.',
    long_description=README,
    url='https://github.com/ninjabit/aldryn-lightslider',
    author='Tobia Ghiraldini',
    author_email='tobia.ghiraldini@ninjabit.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
