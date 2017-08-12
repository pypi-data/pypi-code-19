from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='blobstash-filetree',
    version='0.0.1',
    description='BlobStash FileTree client',
    long_description=long_description,
    author='Thomas Sileo',
    author_email='t@a4.io',
    url='https://github.com/tsileo/blobstash-python-filetree',
    packages=['blobstash.filetree'],
    license='MIT',
    install_requires=[
        'blobstash-base==0.0.2',
        'requests',
    ],
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='blobstash FileTree client',
)
