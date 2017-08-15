from setuptools import setup, find_packages

setup(
	name='Yahoo_Finance_Stock_Ticker',
	packages=find_packages(),
	version='0.0.0',
	description='Web scrapping on Yahoo Finance for stock market prices',
	url='https://github.com/PizzaPat/Yahoo_Finance_Stock_Ticker',
	author='Patrapee Pongtana',
	author_email='patpongtana@gmail.com',
	license='MIT',
	keywords=['yh-ticker'],
	entry_points={
		'console_scripts':[
			'yh-ticker=Yahoo_Finance_Stock_Ticker.main:main'
			]},
	install_requires=['bs4','argparse']
	)