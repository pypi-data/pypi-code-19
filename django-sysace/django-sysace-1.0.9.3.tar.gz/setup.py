import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-sysace',
    version='1.0.9.3',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  
    description='ACE is a Django app to administrate networks hosts, ip address, services, racks, patchpanels, phones and more. The system objective is turn the IT Infraestructure adminsitration easyer.',
    long_description=README,
    url='https://www.rogeriodacosta.com.br/',
    author='Rogerio da Costa Dantas Luiz',
    author_email='rogeriocdluiz@gmail.com',
    install_requires=[
        'django-modalview==0.1.5',
        'django-autocomplete-light==3.1.5',
        'reportlab==2.5',
        'django-simple-history',
        'py2-ipaddress==3.4',
        'pisa==3.0.33',
        'html5lib==1.0b3',
        'Pillow==2.6.1',
        'django-import-export==0.4.5',
        'django-solo==1.1.2',
        'django-mail-templated==2.6.2', 
	'django-widget-tweaks==1.4.1',
	'django-filter==0.14.0',
	'django-pagination==1.0.7',
	'django-mass-edit==2.7', 
	'django-filter==0.14.0',
	'django-widget-tweaks==1.4.1',
	'django-mail-templated==2.6.2',
	'django-solo==1.1.2',
	'django-extensions==1.7.4',
	'django-session-security==2.5.1',

    ],
    setup_requires=[
    ],
) 
