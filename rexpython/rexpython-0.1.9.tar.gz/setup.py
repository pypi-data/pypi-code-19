from distutils.core import setup

setup(
    name='rexpython',
    version='0.1.9',
    author='Anton P. Linevich',
    author_email='anton@linevich.com',
    keywords="rx rxpy rxjava reactive",
    packages=['rexpython', ],
    scripts=[],
    url='http://pypi.python.org/pypi/rexpython/',
    license='LICENSE.txt',
    description='Simple Reactive Extensions (Rx) for Python',
    long_description=open('README.txt').read(),
    install_requires=['tblib'],
    python_requires='>=2.6',
)
