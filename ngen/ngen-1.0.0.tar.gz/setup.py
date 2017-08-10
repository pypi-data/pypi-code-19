from setuptools import setup, find_packages
import ngen


setup(
    author="Anthony",
    name="ngen",
    version=ngen.__version__,
    packages=find_packages(exclude=["test*", ]),
    url="https://github.com/anthonyalmarza/ngen",
    description=(
        "`ngen` is a utility library housing commonly used design patterns."
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords=['singletons', 'parsers', 'transitions', 'timers'],
    install_requires=['six', 'future'],
    extras_require={'dev': ['ipdb', 'mock']},
    include_package_data=True
)
