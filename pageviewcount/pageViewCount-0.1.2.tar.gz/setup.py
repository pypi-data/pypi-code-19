from setuptools import setup,find_packages

setup(
    name='pageViewCount',
    version='0.1.2',
    url='https://github.com/Fiz1994/pageViewCount',
    author='FizLin',
    author_email='fizlbq@gamil.com',
    description='Statistics page number of views ',
    install_requires=[
        "Django >= 1.7",
    ],
    packages=find_packages(),

)
