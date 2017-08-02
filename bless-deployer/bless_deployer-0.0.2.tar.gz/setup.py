from setuptools import setup, find_packages

setup(
    name='bless_deployer',
    version='0.0.2',
    description='Create configurations and deploy Bless to AWS',
    author='Jorge Dias',
    author_email='jorge@mrdias.com',
    url='https://github.com/diasjorge/bless-deployer',
    keywords=['AWS', 'Bless'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    license="FreeBSD License",
    packages=find_packages(exclude=["test*", "data*"]),
    package_data={'bless_deployer': ['data/*.*']},
    install_requires=[
        'boto3',
        'configargparse'
    ],
    zip_safe=False,
    extras_require={
        'dev': [
            'zest.releaser[recommended]'
        ]
    },
    entry_points={
        'console_scripts': [
            'bless-deployer = bless_deployer.__main__:main'
        ]
    },
)
