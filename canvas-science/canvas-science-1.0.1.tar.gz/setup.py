from setuptools import find_packages, setup

setup(
    name='canvas-science',
    version='1.0.1',
    author='Canvas Medical',
    author_email='engineering@canvasmedical.com',
    url='https://github.com/canvas-medical/science-sdk',
    description="Canvas Medical\'s Science SDK",
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
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
