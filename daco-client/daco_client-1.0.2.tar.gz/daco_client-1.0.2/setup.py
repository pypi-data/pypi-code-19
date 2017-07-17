from distutils.core import setup

setup(
    name="daco_client",
    version="1.0.2",

    install_requires=["requests-oauthlib"],

    # metadata for upload to PyPI
    author="andricDu",
    author_email="dusan.andric@oicr.on.ca",
    description="Simple DACO Client Wrapper",
    license="GPLv3",
    keywords="DACO ICGC",
    url="https://github.com/icgc-dcc/Daco-Py",  # project home page, if any
)