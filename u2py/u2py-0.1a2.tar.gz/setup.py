from setuptools import setup,find_packages
setup(
    name='u2py',
    version='0.1a2',
    description='A utility to convert ui files to python files',
    url='https://github.com/dragneelfps/u2py',
    author='Sourabh S. Rawat',
    author_email='dragneelfps@gmail.com',
    license='GPLv3+',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 10'
    ],
    #keyword='ui-files  development',
    packages=find_packages(),
    install_requires=['PyQt5'],
    python_requires='>=3',
    entry_points={
        'console_scripts':[
            'u2py = u2py.__main__:main'
        ]
    },
    # package_data={
    #     'config':['co.cmd']
    # },
    include_package_data=True,
)