from setuptools import setup
from mg_thumbor import __version__

setup(name="mg_thumbor",
    version=__version__,
    description="Extra filters and optimizers for thumbor by MindGeek",
    url="https://github.com/MindGeekOSS/mg_thumbor",
    author="Fabrice Baumann",
    author_email="fabrice.baumann@mindgeek.com",
    license="MIT",
    packages=["mg_thumbor", "mg_thumbor.filters"],
    package_dir={"mg_thumbor": "mg_thumbor"},
    zip_safe=False
)
