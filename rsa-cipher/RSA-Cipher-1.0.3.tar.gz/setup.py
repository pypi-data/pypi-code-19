from setuptools import setup, find_packages

setup(
	name='RSA-Cipher',
	packages=find_packages(),
	version='1.0.3',
	description='Generate encrypted/decrypted text using RSA method',
	author='Patrapee Pongtana',
	author_email='patpongtana@gmail.com',
	license='MIT',
	url='https://github.com/PizzaPat/RSA_Cipher',
	keywords=['RSA'],
	entry_points={
		'console_scripts':[
			'rsa=RSA_Cipher.RSA:main'
			]},
	install_requires=['pyperclip']
)