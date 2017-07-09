from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='spotify_to_google',
      version='0.1',
      description='Imports Spotify playlists into your Google Play Music account',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Topic :: Utilities',
          'Topic :: Internet',
          'Topic :: Multimedia :: Sound/Audio',
      ],
      keywords='spotify playlists google play music import',
      url='http://github.com/coffeemaker2017/spotify_to_google',
      author='Michael Krol',
      author_email='info@michael-krol.de',
      license='MIT',
      packages=['spotify_to_google'],
      scripts=['bin/spotify_to_google_script'],
      entry_points={
          'console_scripts': ['spotify_to_google_script=spotify_to_google.command_line:main'],
      },
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=[
          'spotipy',
          'gmusicapi',
      ],
      include_package_data=True,
      zip_safe=False)