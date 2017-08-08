from distutils.core import setup

setup(
    name='jenkins_cli_tool',
    version='4.0',
    packages=['cli', 'cli.startjob', 'cli.startAndMonitor', 'tests', 'cli.queue'],
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
            'jenkins-cli-tool = cli.cli:entry_point'
        ]
    }
)
