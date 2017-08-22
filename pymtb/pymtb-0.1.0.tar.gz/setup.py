from setuptools import setup, find_packages
import mtb
setup(
    name="pymtb",
    version=mtb.__version__,
    packages=find_packages(),
    author="Mel Massadian",
    description="Mel Tool Box - Personal Library",
    long_description=open('README.md').read(),
    py_modules=["mtb"],
    install_requires=[
        "pyqt5", "sh", "pymediainfo", "timecode", "pillow", "numpy>=1.13"
    ],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',


        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    setup_requires=["numpy"],

    include_package_data=True,
    # data_files=[('assets/fonts/', ['mtb/assets/Akkurat-Mono.otf', 'mtb/assets/Akkurat.otf']),
    #             ('', ['mtb/qtStyles.css'])]

    # entry_point='''
    #     [console_scripts]
    #     hello=hello:cli
    # '''
)
