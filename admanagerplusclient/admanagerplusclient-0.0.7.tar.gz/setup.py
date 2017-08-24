from distutils.core import setup

setup(
    name='admanagerplusclient',
    version='0.0.7',
    author='Jim Barcelona',
    author_email='barce@me.com',
    packages=['admanagerplusclient', 'admanagerplusclient.tests'],
    install_requires=[
      'future',
    ],
    scripts=[],
    url='http://pypi.python.org/pypi/admanagerplusclient/',
    license='LICENSE',
    description='A client for interacting with the Ad Manager Plus Platform.',
    long_description=open('README.txt').read(),
)
 
