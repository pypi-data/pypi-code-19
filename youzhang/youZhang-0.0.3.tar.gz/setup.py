from distutils.core import setup

NAME = 'youZhang'
_MAJOR = 0
_MINOR = 0
_MICRO = 3
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DESCRIPTION = "youtube-download-tools @ZHANG Xu-long"


def long_description():
    readme = open('README.md', 'r').read()
    changelog = open('CHANGELOG.md', 'r').read()
    return changelog + '\n\n' + readme


setup(
    packages=['youZhang'],
    data_files=[('./', ['CHANGELOG.md', 'README.md'])]
    ,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description(),
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    keywords='audio music sound',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    install_requires=['numpy==1.12.1', 'tqdm==4.11.2',
                      'pyPdf==1.13', 'PyYAML==3.12',
                      ],
)
