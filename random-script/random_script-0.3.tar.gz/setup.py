from setuptools import setup, find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))
setup(
    name='random_script',

    version='0.3',

    description='A sample Python project',
    long_description= "empty",

    url='https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=random-script',

    author='Ahmed Maher',
    author_email='ahmed_maher1992@hotmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6'
    ],
	
    keywords='sample setuptools development',
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    py_modules=["random_script"],
    # install_requires=['peppercorn'],
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
    # package_data={
    #     'sample': ['package_data.dat'],
    # },
    # data_files=[('my_data', ['data/data_file'])],
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)