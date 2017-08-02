from setuptools import setup, find_packages

setup(
    name='nemo_plokamos_plugin',
    version="0.0.21",
    packages=find_packages(exclude=["examples", "tests"]),
    url='https://github.com/perseids-project/nemo_plokamos_plugin',
    license='GNU GPL',
    author='Frederik Baumgardt',
    author_email='baumgardt@informatik.uni-leipzig.de',
    maintainer='Bridget Almas',
    maintainer_email='balmas@gmail.com',
    description= "Plugin for Capitains Nemo to load Perseids Plokamos Annotator on passage page",
                 test_suite="tests",
    install_requires=[
        "flask_nemo==1.0.0b3",
        "nemo-oauth-plugin>=0.0.5"
    ],
    tests_require=[
        "flask_nemo==1.0.0b3"
    ],
    include_package_data=True,
    zip_safe=False
)
