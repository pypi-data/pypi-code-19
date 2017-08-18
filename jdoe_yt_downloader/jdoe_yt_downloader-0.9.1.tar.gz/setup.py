from setuptools import setup

setup(name='jdoe_yt_downloader',
	version='0.9.1',
	description='Download YT video in mp3 format',
	url='https://github.com/JohnnyDeeee/YT_MP3_Downloader.git',
	author='JohnDoe',
	author_email='anotherfakeone@live.nl',
	license='MIT',
	packages=['jdoe_yt_downloader'],
	zip_safe=False,
	entry_points={
		'console_scripts': [
			'jdoe_yt_downloader = jdoe_yt_downloader.__main__:main'
		]
	},
	install_requires=[
		'progressbar2',
		'google-api-python-client',
		'argparse'
	])