from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='blobstash-base',
    version='0.0.1',
    description='BlobStash client',
    long_description=long_description,
    author='Thomas Sileo',
    author_email='t@a4.io',
    url='https://github.com/tsileo/blobstash-python-base',
    packages=['blobstash.base'],
    license='MIT',
    install_requires=[
        'requests',
    ],
    python_requires='>=3.4',
)
