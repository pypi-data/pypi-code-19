from setuptools import setup, find_packages
from helga_trade import __version__ as version


setup(
    name="helga-trade",
    version=version,
    description=('Stock, crypto, forex trade information plugin for helga'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
    keywords='irc bot trade',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=['helga', 'requests', 'googlefinance'],
    test_suite='tests/test_trade',
    entry_points=dict(
        helga_plugins=[
            'trade = helga_trade.helga_trade:trade',
        ],
    ),
)
