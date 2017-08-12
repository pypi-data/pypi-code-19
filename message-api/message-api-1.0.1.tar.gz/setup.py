import os.path
from setuptools import setup, find_packages

package_dir = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(package_dir, "version")
with open(version_file) as version_file_handle:
    version = version_file_handle.read()

setup(
    name = "message-api",
    version = version,
    description = "Message API",
    packages = ["message_api"],
    install_requires=["requests"],
    url = 'https://github.com/message-api/message-api-python',
    keywords = ['channel', 'api', 'message'],
    classifiers = []
)
