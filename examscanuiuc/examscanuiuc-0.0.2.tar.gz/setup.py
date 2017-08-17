
from __future__ import print_function

# Needs:
#  pdftk
#  pdfimages
#  pdftoppm
#  zbar

import os
try:
	from setuptools import setup
except ImportError:
	print('Unable to import setuptools, using distutils instead.')
	from distutils.core import setup

this_directory = os.path.dirname(__file__)
source_directory = os.path.join(this_directory, 'source')
exec(open(os.path.join(source_directory, 'version.py')).read())  # Load in the variable __version__.

setup(
	name='examscanuiuc',
	version=__version__,
	description='For added tags to and processing scanned exams.',
	author='Mark Bell',
	author_email='mcbell@illinois.edu',
	url='https://bitbucket.org/Mark_Bell/examscanuiuc',
	# Remember to update these if the directory structure changes.
	packages=[
		'examscanuiuc',
		'examscanuiuc.demo',
		'examscanuiuc.doc',
		'examscanuiuc.tag',
		'examscanuiuc.scan',
		],
	package_dir={'examscanuiuc': source_directory},
	package_data={
		'examscanuiuc.demo': ['*.pdf', '*.conf', '*.html', '*.xlsx'],
		'examscanuiuc.doc': ['examscanuiuc.pdf'],
		},
	install_requires=[
		# tag requirements.
		'reportlab',
		'qrcode',
		'pillow',
		'PyPDF2',
		'openpyxl',
		# scan requirements.
		'numpy',
		'scipy',
		'scikit-image',
		'pandas',
		'xlrd',
		'libzbar-cffi',
		'jinja2',
		'weasyprint',
		'matplotlib',
		]
	)

