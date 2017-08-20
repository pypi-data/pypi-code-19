from setuptools import setup, find_packages

setup(
        name='portfoliomanager',
        version='0.1',
        description='Tracks N number of investments equally weighted against IVV etf.',
        url='https://github.com/JamesWhiteleyIV/Portfolio-Manager',
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
        keywords='investment utility pandas portfolio management',
        packages=find_packages(exclude=['docs', 'tests*']),
        install_requires=['investmentutility'] #these get installed before this package
        )
