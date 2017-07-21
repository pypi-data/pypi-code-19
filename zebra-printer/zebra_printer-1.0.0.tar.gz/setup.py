try:
    from setuptools import setup
except:
    from distutils.core import setup
setup (
    name = 'zebra_printer',
    version = '1.0.0',
    py_modules = ['zebra_print'],
    author = 'shock1974',
    author_email = 'han@inhand.com.cn',
    url = 'https://github.com/hanchuanjun/zebra-print-service',
    description = 'a tool for zebra printer',
    license="MIT",
    install_requires=[
		'pyserial==3.3'
	],
)