from setuptools import setup

setup(name='dsbox-dataprofiling',
      version='0.1.3',
      url='https://github.com/usc-isi-i2/dsbox-profiling.git',
      maintainer_email='kyao@isi.edu',
      maintainer='Ke-Thia Yao',
      description='DSBox data preprocssing tools for profiling data',
      license='MIT',
      packages=['dsbox', 'dsbox.datapreprocessing', 'dsbox.datapreprocessing.profiler'],
      zip_safe=False,
      install_requires=['pandas', 'langdetect']
      )
