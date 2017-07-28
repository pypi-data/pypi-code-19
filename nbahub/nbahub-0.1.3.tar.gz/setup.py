from distutils.core import setup


setup(
    name="nbahub",
    packages=['nbahub', "nba_stats_api"],
    package_data={'nba_stats_api': ["data/bbref_id_map.json"]},
    install_requires=["nba_py",
                      "requests==2.18.1",
                      "click==6.7",
                      "beautifulsoup4==4.6.0",
                      # Weird...
                      "html5lib==0.999999999",
                      "openpyxl==2.4.8"],
    version="0.1.3",
    license="BSD 3-clause",
    description="A CLI application that gathers NBA stats from various sources and aggregates them.",
    author="John Griebel",
    author_email="johnkgriebel@gmail.com",
    url="https://github.com/johngriebel/nbahub",
    download_url="https://github.com/johngriebel/nbahub/archive/0.1.tar.gz",
    keywords=["nba", "statistics"],
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python :: 3.6'],
    entry_points={
        'console_scripts': ["nbahub=nbahub.nbahub_cli:main"]
    }
)
