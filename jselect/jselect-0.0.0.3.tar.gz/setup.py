from setuptools import setup, find_packages
import jselect

setup(
    name='jselect',
    version=jselect.__version__,
    author='guan ming',
    author_email='i@guanming.me',
    url='https://github.com/lennon-guan/jselect',
    packages=find_packages(),
    install_requires=['ply>=3.0.0'],
    description='A tools that helps you to select data from json file',
    entry_points=dict(
        console_scripts=[
            'jselect = jselect.cmd:cmd',
        ],
    ),
)
