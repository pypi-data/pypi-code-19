from distutils.core import setup
from setuptools import find_packages

INSTALL_REQUIREMENTS = [
    'Django>=1.10.5',
    'Markdown==2.6.8',
    'sexpdata==0.0.3',
]

setup(
    name='pcart-script',
    version='2.0',
    author='Oleh Korkh',
    author_email='oleh.korkh@the7bits.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    license='BSD License',
    description='A powerful e-commerce solution for Django CMS',
    long_description=open('README.txt').read(),
    platforms=['OS Independent'],
    url='http://the7bits.com/',
    install_requires=INSTALL_REQUIREMENTS,
)
