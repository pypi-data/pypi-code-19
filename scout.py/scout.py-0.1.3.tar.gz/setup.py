import versioneer

from setuptools import setup, find_packages

setup(
    name="scout.py",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "requests"
    ],
    author="datawire.io",
    author_email="dev@datawire.io",
    url="https://github.com/datawire/scout.py",
    download_url="https://github.com/datawire/scout.py/tarball/{}".format(versioneer.get_version()),
    keywords=[],
    classifiers=[],
)
