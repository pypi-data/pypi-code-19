from distutils.core import setup

setup(
    name='license_lister',
    packages=['license_lister'],
    install_requires=[
        'yolk3k>=0.9',
        'gevent>=1.2.2'
    ],
    version='0.1.0',
    platforms='any',
    description='List licenses for external packages in use by your Python code',
    author='Jon Kronander',
    author_email='jonkronander@gmail.com',
    url='https://github.com/jonkr/license_lister',
    download_url='https://github.com/jonkr/license_lister/archive/0.1.0.tar.gz',
    keywords=['license', 'licenses'],
    classifiers=[],
    entry_points={
        'console_scripts': [
            'license_lister = license_lister.__main__:main'
        ]
    },
)
