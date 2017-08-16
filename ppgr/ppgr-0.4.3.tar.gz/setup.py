from distutils.core import setup

with open("VERSION", "r") as f:
    VERSION = f.readline().strip()

setup(
    name="ppgr",
    packages=["ppgr"],
    version=VERSION,
    description="Python Piped GRapher",
    author="Maximilian Remming",
    author_email="maxremming@gmail.com",
    url="https://github.com/PolarPayne/ppgr",
    download_url="https://github.com/PolarPayne/ppgr/archive/{}.tar.gz".format(VERSION),
    license="MIT",
    entry_points={
          'console_scripts': [
              'ppgr = ppgr.__main__:main'
          ]
      },
    keywords=["cli", "graphing"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ]
)
