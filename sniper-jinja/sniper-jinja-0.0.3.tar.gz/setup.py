from setuptools import setup

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

with open('pip-req.d/install.txt') as f:
    install_requires = []

    for line in f:
        if '#' in line:
            # remove comment
            line = line[:line.index('#')]

        line = line.strip()

        if line:
            install_requires.append(line)


setup(
    name="sniper-jinja",
    version="0.0.3",
    description="a jinja2 plugin for sniper",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/lexdene/sniper-jinja",
    license='GPLv3',
    author="Elephant Liu",
    author_email="lexdene@gmail.com",
    packages=['sniper_jinja'],
    platforms=['any'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
