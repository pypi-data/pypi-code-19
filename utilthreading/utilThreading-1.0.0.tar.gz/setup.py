from setuptools import setup
import utilThreading


setup(
    name='utilThreading',
    version=utilThreading.__version__,
    description='A collection of classes which execute common tasks that require execution on an additional threads.',
    long_description=open('README.md').read(),
    packages=['utilThreading'],
    license='MIT',
    url='https://github.com/seanwiseman/util-threading',
    maintainer='Sean Wiseman',
    maintainer_email='seanwiseman2012@gmail.com',
)

