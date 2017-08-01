from setuptools import setup

#with open('requirements.txt', 'r') as fh:
#    dependencies = [l.strip() for l in fh]

setup(
    name='reframe',
    description='Relational algebra on top of Pandas DataFrames ',
    version='1.0.1',
    py_modules = ['reframe'],
    author = 'Brad Miller',
    author_email = 'bonelake@mac.com',
    install_requires= ['pandas>=0.16.0'],
    include_package_data = False,
    license='GPL',
    url = 'https://github.com/bnmnetp/reframe',
    keywords = ['database', 'relational'], # arbitrary keywords
    long_description=open('README.rst').read(),
)
