from setuptools import setup, find_packages

setup(
    name="endpointer",
    description='A tool for transforming OpenAPI v3 specifications\
        into endpoint documentation',
    license="MIT",
    version='0.0.3',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['api','documentation', 'OpenAPI'],
    install_requires=[
        'pyyaml',
    ],
    extras_require={
        'dev': [
            'pylint',
        ]
    },
    python_requires='~=3.6',
)
