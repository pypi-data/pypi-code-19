from distutils.core import setup

setup(
    name='appvey',
    version='1',
    author='anatoly techtonik <techtonik@gmail.com>',
    url='https://github.com/techtonik/appvey',

    description='Kick AppVeyor builds',
    license='Public Domain',

    py_modules=['appvey'],

    install_requires = '''
requests
shellrun
''',
    entry_points = {
        'console_scripts': ['appvey=appvey:main'],
    },

    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
