from setuptools import setup

setup(
    name = 'logscli',
    version = '0.1.0',
    author = 'Karolis Mazukna',
    author_email = 'karolis@zenedge.com',
    url = 'https://github.com/zenedge/logs_cli',
    packages = ['logscli'],
    entry_points = {
        'console_scripts': [
            'logscli = logscli.__main__:main'
        ]
    },
    install_requires = {
      'pyaml',
      'click'
    }
)
