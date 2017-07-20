from setuptools import setup

setup(
    name="uinames",
    packages=["uinames"],
    version="1.0.0",
    description="A light Python wrapper for the UINames API",
    author="Harry Lewis",
    author_email="harry.lewis@queensu.ca",
    url="https://github.com/harrylewis/python-uinames",
    keywords=["testing", "mock", "data", "users"],
    install_requires=["requests==2.13.0", "responses==0.5.1", "nose==1.3.7"]
)
