import os
from setuptools import setup

# clouddistrict
# Generate occupants and occupations for your custom village, town or city! (for D&D purposes or related) (please do not imbibe clouddistrict while under the influence of other medications)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="clouddistrict",
    version="0.0.1",
    description="Generate occupants and occupations for your custom village, town or city! (for D&D purposes or related) (please do not imbibe clouddistrict while under the influence of other medications)",
    author="Johan Nestaas",
    author_email="johannestaas@gmail.com",
    license="GPLv3+",
    keywords="",
    url="https://www.bitbucket.org/johannestaas/clouddistrict",
    packages=['clouddistrict'],
    package_dir={'clouddistrict': 'clouddistrict'},
    long_description=read('README.rst'),
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'clouddistrict=clouddistrict:main',
        ],
    },
    zip_safe=False,
    package_data={
        'clouddistrict': ['names/*.txt'],
    },
    include_package_data=True,
)
