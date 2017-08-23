from setuptools import setup

exec (open('dashgrid/version.py').read())

setup(
    name='dashgrid',
    version=__version__,
    author='',
    packages=['dashgrid'],
    include_package_data=True,
    license='MIT',
    description='Dash UI component suite',
    install_requires=[]
)
