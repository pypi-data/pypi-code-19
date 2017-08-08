from setuptools import setup

setup(
    name='rnapk',
    version='0.10',
    description='A simple utility to send React Native APKs via email.',
    py_modules=['main'],
    install_requires=[
        'Click',
        'PyYaml'
    ],
    entry_points='''
        [console_scripts]
        rnapk=main:cli
    ''',
    url='https://github.com/srishanbhattarai/rnapk',
    author='Srishan Bhattarai',
    author_email='srishanbhattarai@gmail.com',
    license='MIT',
    include_package_data=True
)
