from distutils.core import setup

NAME = 'pyTvocal'
_MAJOR = 0
_MINOR = 0
_MICRO = 2
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DESCRIPTION = "A python tutorial for vocal detection @ZHANG Xu-long"


def long_description():
    readme = open('README.md', 'r').read()
    changelog = open('CHANGELOG.md', 'r').read()
    return changelog + '\n\n' + readme


setup(
    packages=['pyTvocal'],
    data_files=[('./', ['CHANGELOG.md', 'README.md']), ],
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description(),
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    keywords='vocal',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    install_requires=['numpy',
                      'h5py',
                      'pydub',
                      'scikit-learn',
                      'Keras==1.2.2',
                      ],
)
