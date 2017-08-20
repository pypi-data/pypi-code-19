from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='gurka_toolkits',
	version=__import__('gurka').__version__,
	description='Contains a set of helper kits that can help you for development.',
	long_description=readme(),
	url='http://github.com/yanwarsolah/gurka_toolkits',
	include_package_data=True,
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Topic :: Software Development :: Libraries'
	],
	author='Yanwar Solahudin',
	author_email='yanwarsolah@gmail.com',
	license='MIT',
	packages=['gurka'],
	test_suite='nose.collector',
	tests_require=['nose'],
	zip_safe=False)

