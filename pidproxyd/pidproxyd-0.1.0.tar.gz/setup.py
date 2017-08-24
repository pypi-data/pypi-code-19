import setuptools

setuptools.setup(
    name="pidproxyd",
    version="0.1.0",
    url="https://github.com/ajpen/pidproxyd",

    author="Anfernee Jervis",
    author_email="anferneejervis@gmail.com",

    description="A pidproxy for supervisord that supports daemonized processes.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'pidproxyd = pidproxyd:main',
        ],
    },
)
