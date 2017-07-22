from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='greenscreen_control',
    version='0.0.1',
    license='Apache Software License',
    url='https://github.com/dermotduffy/greenscreen_control',
    author='Dermot Duffy',
    author_email='dermot.duffy@gmail.com',
    description='Python module, server and utility to control greenscreen.',
    long_description=long_description,
    packages=find_packages(),
    keywords='greenscreen chromecast cast',
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
			'PyChromecast>=0.8.1',
      'Twisted>=16.0.0',
		],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points = {
        'console_scripts': [
            'greenscreen_control=greenscreen_control.greenscreen_control_cli:main',
            'greenscreen_control_server=greenscreen_control.greenscreen_control_server:main',
        ],
    },
)
