from setuptools import setup

setup(
    name='trstringerpypitest',
    packages=['trstringerpypitest'],
    version='0.1.5',
    description='Testing and showing demo and sample',
    author='Thomas Stringer',
    author_email='me@trstringer.com',
    url='https://github.com/tstringer/pypitestpkg',
    keywords=['testing'],
    classifiers=[],
    install_requires=[
        'azure-mgmt-compute~=2.0.0',
        'azure-mgmt-network~=1.3.0',
        'azure-mgmt-storage~=1.1.0',
        'azure-mgmt-resource~=1.1.0',
        'azure-cli-core~=2.0.12'
    ]
)
