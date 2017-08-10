from setuptools import setup

setup(
    name='azure-ansible-base',
    version='0.1.3',
    description='Azure SDK dependencies for Ansible Azure modules',
    author='Thomas Stringer',
    author_email='me@trstringer.com',
    url='https://github.com/tstringer/azure-ansible-base',
    keywords=['azure'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'azure-mgmt-compute~=2.0.0',
        'azure-mgmt-network~=1.3.0',
        'azure-mgmt-storage~=1.2.0',
        'azure-mgmt-resource~=1.1.0',
        'azure-storage~=0.35.1',
        'azure-cli-core~=2.0.12',
        'msrestazure~=0.4.11'
    ]
)
