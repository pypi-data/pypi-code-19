from setuptools import setup

setup(
    name='zekeconv',
    version='0.1.0',
    description='converter between zeke dumps and directory structures',
    author='Stanislav Klenin',
    author_email='stanislav.klenin@gmail.com',
    license='Apache Software License',
    packages=['zekeconv'],
    entry_points={
        'console_scripts': [
            'zekeconv = zekeconv.zekeconv:main'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose'],
)
