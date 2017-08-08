from distutils.core import setup

setup(
    name='jenkins-cli-tool',
    version='4.2',
    packages=['cli', 'cli.startjob', 'cli.startAndMonitor', 'tests', 'cli.queue', 'tool_library'],
    url='https://git.ecd.axway.int/apigw-champions/jenkins-cli',
    license='MIT',
    author='chermet',
    author_email='chermet@axway.com',
    description='CLI tool for Jenkins',
    install_requires=[
       'click',
       'python-jenkins'
    ],
    entry_points={
        'console_scripts': [
            'tool_library = cli.cli:entry_point'
        ]
    }
)
