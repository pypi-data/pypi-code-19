import setuptools

setuptools.setup(
    name="nbsolutions",
    version='0.1.1',
    author="Jacky Lu",
    author_email="jackylu97@gmail.com",
    url="https://github.com/jackylu97/nbsolutions",
    download_url="https://github.com/jackylu97/nbsolutions/archive/0.1.1.tar.gz",
    description="Simple Jupyter extension that allows the user to mark solution cells",
    packages= ["nbsolutions"],
    install_requires=[
        'notebook',
    ],
    package_data={'nbsolutions': ['static/*']},
)
