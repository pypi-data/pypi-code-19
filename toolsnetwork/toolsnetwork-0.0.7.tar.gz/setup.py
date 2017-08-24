from setuptools import setup, find_packages

setup(name='toolsnetwork',
      version='0.0.7',
      description='A very simple networking library for seperating MAC Frame written by Rohit G Bal (@rohitgbal).',
      url='https://sites.google.com/site/rohitgbal/',
      maintainer='Rohit G BAl',
      maintainer_email='rohitgbal@gmail.com',
      author='Rohit G Bal',
      author_email='rohitgbal@gmail.com',
      license='MIT Lisence',
      py_modules=['toolsnetwork'],
      zip_safe=False,
      keywords=["MAC", "IPv4", "IPv6"],
      packages=find_packages(include=["toolsnetwork","toolsnetwork.*",]),
      include_package_data=True
    )
	