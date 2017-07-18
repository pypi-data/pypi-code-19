from setuptools import setup, PackageFinder

import jtranslate

setup(
    name='jtranslate',
    version=jtranslate.__version__,
    packages=PackageFinder.find(exclude=['examples', 'python']),
    url='https://bitbucket.org/illemius/jtranslator',
    license='MIT',
    author='illemius / Alex Root Junior',
    author_email='illemius@gmail.com',
    description='',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'babel',
        'pyyaml'
    ]
)
