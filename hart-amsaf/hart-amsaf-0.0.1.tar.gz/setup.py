from setuptools import setup

setup(name='hart-amsaf',
      version='0.0.1',
      description='The HART Lab Automated MRI Segmentation and Analysis Framework',
      url='https://github.com/iancmcdonald/AMSAF',
      author='Ian McDonald and Daniel Ho',
      author_email='ian.c.mcdonald@berkeley.edu',
      license='MIT',
      keywords='hart, hart-amsaf, HartAmsaf, amsaf, segmentation, mri, medical',
      packages=['HartAmsaf'],
      install_requires=['scipy', 'numpy', 'scikit-learn'],
      zip_safe=False)
