from setuptools import setup
import os

setup(
        name='Data-viz',
        version='0.8.4dev',
        packages=['data_viz'],
        description='Represents your high-dimensional datas in a 2D space and play wih it',
        long_description = open('data_viz/README.md').read(),
        install_requires = open('data_viz/requirements/requirements.txt').read(),
        license = 'GPL V3',
        author='Sofian Medbouhi',
        author_email='sof.m.sk@free.fr',
        )
            
