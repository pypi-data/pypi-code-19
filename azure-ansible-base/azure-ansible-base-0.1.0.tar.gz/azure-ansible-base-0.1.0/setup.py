from setuptools import setup

setup(
    name='azure-ansible-base',
    version='0.1.0',
    description='Azure SDK dependencies for Ansible Azure modules',
    author='Thomas Stringer',
    author_email='me@trstringer.com',
    url='https://github.com/tstringer/azure-ansible-base',
    keywords=['azure'],
    classifiers=[],
    install_requires=[
        'azure-mgmt-compute~=2.0.0',
        'azure-mgmt-network~=1.3.0',
        'azure-mgmt-storage~=1.1.0',
        'azure-mgmt-resource~=1.1.0',
        'azure-cli-core~=2.0.12'
    ]
)
