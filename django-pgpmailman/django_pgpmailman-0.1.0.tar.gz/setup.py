from setuptools import find_packages, setup

setup(
        name='django_pgpmailman',
        version='0.1.0',
        description='A web interface for the GNU Mailman PGP plugin.',
        long_description="""\
A web interface for the Mailman PGP plugin.""",
        author='Jan Jancar',
        author_email='johny@neuromancer.sk',
        license='GPLv3',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: System Administrators',
            'Operating System :: POSIX',
            "Programming Language :: Python :: 2",
            'Topic :: Communications :: Email :: Mailing List Servers',
        ],
        keywords='email mailman django pgp',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        install_requires=[
            'Django>=1.8',
            'Django<1.12',
            'django_mailman3',
            'mailmanclient>=3.1.1',
            'PGPy>=0.4.2'
        ],
        dependency_links=[
            'https://github.com/J08nY/PGPy/archive/dev.zip#egg=PGPy-0.4.2',
            'https://gitlab.com/J08nY/mailmanclient/repository/archive.tar.gz?ref=plugin#egg=mailmanclient-3.1.1'
        ]
)
