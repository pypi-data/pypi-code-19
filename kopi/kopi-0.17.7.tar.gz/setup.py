#!python3
from setuptools import setup

setup(
   name='kopi',
   version='0.17.7',
   description='Create publication quality graph in pdf format using CSON(CoffeeScript-Object-Notation)',
   author='CHEN, Lee Chuin',
   author_email='leechuin@gmail.com',
   license='MIT',
   python_requires='>=3',
   classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
   keywords='plot graph pdf cson',
   packages=['kopi'],  #same as name
   install_requires=['numpy','pillow'], #external packages as dependencies
)
