from setuptools import setup, find_packages


setup(
    name='cobrascraper',
    packages=find_packages(),
    version='0.0.2',
    description='Dymanic & scalable web scraping system',
    author='Eddy Hintze',
    author_email="eddy@hintze.co",
    url="https://github.com/xtream1101/cobra",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=['lxml',
                      'cssselect',
                      ]
)
