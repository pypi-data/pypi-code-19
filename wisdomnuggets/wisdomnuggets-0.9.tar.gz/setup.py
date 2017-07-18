from setuptools import setup

def readme():
	with opne('README.rst') as f:
		return f.read()

setup(name='wisdomnuggets',
	version='0.9',
	description='The wisest maxim in the world',
	url='https://github.com/ss1921',
	author='1921Designs',
	author_email='im1921designs@gmail.com',
	license='MIT',
	packages=['wisdomnuggets'],
	install_requires=['markdown'],
	include_package_data=True,
	zip_safe=False,
	scripts=['bin/wisest_maxim'],
	test_suite='nose.collector',
	tests_require=['nose'],
	)