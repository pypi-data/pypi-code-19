from setuptools import setup

setup(name='smartpath',
	version='0.11',
	description='smartpath implements the SmartFileSystem class (and connector classes) to provide unified object-oriented access to filesystems of various protocols.  It draws a number of parallels to the Windows FileSystemObject',
	url='http://github.com/miking7/smartpath',
	author='Michael Engelbrecht',
	author_email='michaelndani@gmail.com',
	license='MIT',
	packages=['smartpath'],
	package_data={'smartpath': ['php/*']},
	zip_safe=False)
