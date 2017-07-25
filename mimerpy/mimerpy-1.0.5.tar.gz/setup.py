from setuptools import setup, find_packages
from distutils.core import Extension

extensions = [
    Extension('connection', include_dirs = ['/usr/include'],
                                            library_dirs = ['/usr/include'],
                                            libraries = ['mimmicroapi'],
                                            sources = [
                                                  "src/cursor.c",
                                                  "src/connection.c",
                                                    ]),
    Extension('cursor', include_dirs = ['/usr/include'],
                                            library_dirs = ['/usr/includelib'],
                                            libraries = ['mimmicroapi'],
                                            sources = [
                                            "src/cursor.c",
                                            "src/connection.c"
                                              ])
]


setup (
    name='mimerpy',
    version='1.0.5',
    description='A sample Python project',
    long_description='A sample Python project',
    #url='www.mimer.com',
    #download_url='www.developer.mimer.com/python/download',
    author='Erik Gunne & Magdalena Bostrom',
    author_email='erik.gunne@mimer.com',
    maintainer = 'Erik Gunne & Magdalena Bostrom',
    maintainer_email = 'oklart@mimer.com',
    license='MIT',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='MimerSQL DB',
    ext_modules = extensions,
    packages=['mimerpy'],
    package_dir={'mimerpy': 'mimerpy', 'mimerpy.tests': 'tests'},
    python_requires='>=3',
    #install_requires=['Mimer>=11.0']
    )
