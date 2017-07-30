from distutils.core import setup
setup(
    name='webnsock',
    packages=['webnsock'],
    package_data={'webnsock': ['www/*', 'www/*/*', 'www/*/*/*', 'www/*/*/*/*']},
    version='0.0.1',
    description='A web.py and websocket framework for interactive webservices',
    author='Marc Hanheide',
    author_email='marc@hanheide.net',
    url='https://github.com/marc-hanheide/webnsock',  # use the URL to the github repo
    download_url='https://github.com/marc-hanheide/webnsock/archive/0.4.tar.gz',  # I'll explain this in a second
    keywords=['web.py', 'websockets', 'webserver'],  # arbitrary keywords
    classifiers=[],
)
