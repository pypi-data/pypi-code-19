from setuptools import setup

setup(name='tsputil',
      version='1.1.0a1',
      description=' Helper functions to work with .tsp and .sol files in the context of the Traveling Salesperson Problem',
      url='https://TimRach@bitbucket.org/TimRach/tsp-python.git',
      author='Tim Rach',
      author_email='tim.rach91@gmail.com',
      license='CC BY-SA 3.0',
      packages=['tsputil'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Utilities',
          'Programming Language :: Python :: 3.5',
      ],
      keywords='TSP utilities',
      python_requires='>=3',
      zip_safe=False)
