from setuptools import setup, find_packages

with open("qth_gc/version.py", "r") as f:
    exec(f.read())

setup(
    name="qth_gc",
    version=__version__,
    packages=find_packages(),

    # Metadata for PyPi
    url="https://github.com/mossblaser/qth_gc",
    author="Jonathan Heathcote",
    description="Deletes Qth properties and other retained MQTT messages "
                "with which no client is affiliated.",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="mqtt asyncio home-automation messaging",

    # Requirements
    install_requires=["qth>=0.3.0"],
    
    # Scripts
    entry_points={
        "console_scripts": [
            "qth_gc = qth_gc:main",
        ],
    }
)
