from setuptools import setup, find_packages

setup(
        name='investmentutility',
        version='0.1.1',
        description='Useful functions for building investment applications.',
        url='https://github.com/JamesWhiteleyIV/Investment-Utility',
        author='James Whiteley IV',
        author_email='jameswhiteleyiv@gmail.com',
        license='MIT',
        classifiers=[
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            ],
        keywords='investment utility pandas',
        packages=find_packages(exclude=['docs', 'tests*']),
        install_requires=['pandas', 'pandas-datareader', 'numpy', 'matplotlib'] #these get installed before this package
        )
