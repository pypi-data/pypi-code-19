from setuptools import setup

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
    
setup(name='tmdbv3api',
      version='0.4',
      description='A simple wrapper for the TMDb API.',
      long_description=long_descr,
      url='https://github.com/AnthonyBloomer/tmdbv3api',
      author='Anthony Bloomer',
      author_email='ant0@protonmail.ch',
      license='MIT',
      packages=['tmdbv3api'],
      install_requires=[
                'requests'
            ],
            classifiers=[
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                "Topic :: Software Development :: Libraries",
                'Programming Language :: Python :: 2.7'
            ],
      zip_safe=False)
