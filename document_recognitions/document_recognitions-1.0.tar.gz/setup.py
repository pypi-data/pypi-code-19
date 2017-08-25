from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='document_recognitions',
    version='1.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'pytils==0.3',
        'Pillow==4.2.1',
        'chardet==3.0.4',
        'PyPDF2==1.26.0',
        'Wand==0.4.4',
        'python-magic==0.4.13',
    ]
)
