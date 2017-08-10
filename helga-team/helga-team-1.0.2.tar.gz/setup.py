from setuptools import setup, find_packages
from helga_team import __version__ as version


setup(
    name="helga-team",
    version=version,
    description=('Team plugin to track candidates and interview process'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
    keywords='irc bot team',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=['helga', ],
    test_suite='tests/test_team',
    entry_points=dict(
        helga_plugins=[
            'team = helga_team.helga_team:team',
        ],
    ),
)
