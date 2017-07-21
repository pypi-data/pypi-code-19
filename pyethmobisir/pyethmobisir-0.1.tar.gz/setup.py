try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pyethmobisir',
    version='0.1',
    description='ethereum JSON-RPC client',
    long_description=open('README.rst').read(),
    author='balakrishnan',
    author_email='krishnasmartt@gmail.com',
    url='https://github.com/balakrishnan2/pyethmobisir',
    packages=['pyethmobisir'],
    license='Unlicense',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
    install_requires=[
        'ethereum==1.0.8',
        'requests==2.9.1',
    ],
)
