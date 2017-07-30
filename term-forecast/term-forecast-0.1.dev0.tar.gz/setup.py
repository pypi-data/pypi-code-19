from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
	name='term-forecast',
	version='0.1.dev0',
	author='Kevin Midboe',
	author_email='support@kevinmidboe.com',
	
	description='Terminal Forcast is a easily accessible terminal based weather forecaster',
	url='https://github.com/KevinMidboe/termWeather/',
	license='MIT',
	
	packages=['term_forecast'],

	classifiers = [
		"Environment :: Console",
        "Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",

        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
    ],

    install_requires=requirements,

    entry_points={
       'console_scripts': [
           'forecast = term_forecast.term_weather:main',
       ],
    }
)