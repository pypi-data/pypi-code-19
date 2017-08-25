#!/usr/bin/env python3

from os import path
from setuptools import setup

HERE = path.abspath(path.dirname(__file__))

try:
	with open(path.join(HERE, 'README.md')) as f:
		description = f.read()
except:
	description = ''

setup(
	name='jasper-sys',
	version='0.2.4',
	description='Jasper is a system designed to supervise your programs that need to be kept running.',
	long_description=description,
	url='https://github.com/fabiocody/jasper.git',
	author='Fabio Codiglioni',
	author_email='fabiocody@icloud.com',
	license='MIT',
	classifiers=[
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Development Status :: 4 - Beta'
	],
	keywords='jasper, system, process monitor',
	py_modules=['jaspercore', 'jasperctl'],
	install_requires=['psutil', 'bottle', 'requests'],
	entry_points={
		'console_scripts': [
			'jasperctl=jasperctl:main',
		],
	}
)
