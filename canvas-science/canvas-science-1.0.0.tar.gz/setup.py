from setuptools import find_packages, setup

setup(
    name='canvas-science',
    version='1.0.0',
    author='Canvas Medical',
    author_email='engineering@canvasmedical.com',
    url='https://github.com/canvas-medical/science-sdk',
    description="Canvas Medical\'s Science SDK",
    long_description=open('README.md').read(),
    keywords='healthcare science sdk ehr',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Environment :: Web Environment',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',

        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Libraries',
    ],
    packages=find_packages(),
    install_requires=[
        'arrow>=0.10',
        'requests>=2.18',
    ])
