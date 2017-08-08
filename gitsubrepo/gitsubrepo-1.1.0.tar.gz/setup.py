from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="gitsubrepo",
    version="1.1.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=open("requirements.txt", "r").readlines(),
    url="https://github.com/wtsi-hgi/python-git-subrepo",
    license="MIT",
    description="Provides access to `git subrepo` in Python",
    long_description=read_markdown("README.md")
)
