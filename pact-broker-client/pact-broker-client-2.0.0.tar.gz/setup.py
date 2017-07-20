from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='pact-broker-client',
    version='2.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'pull_pact=pact_broker.cli:pull_pact',
            'push_pact=pact_broker.cli:push_pact'
        ]
    },
    license='Apache 2.0',
    author='Babylon Health',
    author_email='chatbot-developers@babylonhealth.com'
)
