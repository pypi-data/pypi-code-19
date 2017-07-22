try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    long_description = open('README.md').read()
except IOError:
    long_description = ""

setup(
    name='soundcloud-python-sdk',
    version='1.0.0',
    description="SoundCloud API python client",
    long_description=long_description,
    url='https://github.com/rohitkhatri/soundcloud-python-sdk',
    author='Rohit Khatri',
    author_email='developer.rohitkhatri@gmail.com',
    license='MIT',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.5',
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords="soundcloud api python sdk",
    packages=['soundcloud'],
    install_requires=["requests"],
)
