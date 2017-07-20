import chewrap
import setuptools

setuptools.setup(
    name='chewrap',
    version=chewrap.__version__,
    packages=['chewrap'],
    entry_points={
        'console_scripts': [
            'che = chewrap.__main__:main',
        ],
    },
    description=chewrap.__doc__,
    package_data={
        'chewrap': ['arguments.json']
    },
    include_package_data=True,
    author='Tom Stoneham',
    license='MIT',
    keywords='eclipse che docker',
    url='https://github.com/tomstoneham/chewrap',
    download_url='https://github.com/tomstoneham/chewrap',
    tests_require=[
        'pytest'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Systems Administration'
    ]
)
