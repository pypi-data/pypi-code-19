from setuptools import setup, find_packages

REQUIRES = (
    'attrs>=17.2.0'
)

setup(
    name='terra-py',
    description='generate terraform json',
    version='0.0.0',
    packages=find_packages(),
    install_requires=REQUIRES,
    author='dmr',
    author_email='dradetsky@gmail.com',
    license='WTFPL',
    keywords=['terraform', 'hcl'],
    entry_points={
        'console_scripts': [
            'terrapy=terrapy.wrap:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: Freely Distributable',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Code Generators',
        'Topic :: System :: Systems Administration',
    ]
)
