from setuptools import setup
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(name='FaceExtractor',
      version='0.1.2',
      description='Extract faces from images with OpenCV',
      url='https://github.com/ducthienbui97/FaceExtractor',
      author='Thien Bui',
      author_email='thienbui797@gmail.com',
      license='BSD-3-Clause',
      packages=['face_extractor'],
      install_requires=['opencv-python'],
      package_data={'face_extractor':['data/*.xml']},
      long_description=long_description,
)