from setuptools import setup, find_packages
setup(
    name="London Borough Tagger",
    version="0.1",
    packages=find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['numpy', 'matplotlib'],


    # metadata for upload to PyPI
    author="Zack Akil",
    author_email="zack.akil@pivigo.com",
    description="Tool for tagging coordinates with the London borough they are within.",
    license="MIT",
    keywords="london borough tag tagger coordinates",
)