from setuptools import setup

setup(
    name="http_client",
    version="0.1.16",
    description="Fast and robust HTTP client based on PyCurl",
    url="https://github.com/huynhminhson/http_client",
    author="Son Huynh",
    author_email="minhsonftu@gmail.com",
    license="MIT",
    packages=["http_client"],
    install_requires=["pycurl", "six"],
)
