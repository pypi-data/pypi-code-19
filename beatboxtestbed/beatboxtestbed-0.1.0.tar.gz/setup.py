import os
from setuptools import setup

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(name='beatboxtestbed',
      description='background error analysis testbed with box models',
      long_description=read('README.rst') + '\n\n' + read('INSTALL.rst') + '\n\n' + read('CHANGES.rst'),
      version='0.1.0',
      url='https://boxmodeling.meteo.physik.uni-muenchen.de',
      author='Christoph Knote, Jerome Barre',
      author_email='christoph.knote@physik.uni-muenchen.de, barre@ucar.edu',
      license='GPLv3',
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2 :: Only',
            'Topic :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Utilities'
        ],
      keywords='',
      python_requires='<3',
      packages=['beatboxtestbed'],
      install_requires=['numpy', 'frappedata', 'tuv', 'chemspectranslator', 'boxmox', 'genbox'],
      entry_points={
          'console_scripts': [
              'make_BEATBOX_cycling_run = beatboxtestbed._console:makeCyclingRun',
              'plot_BEATBOX_assim_diags = beatboxtestbed._console:plotAssimDiags',
              'plot_BEATBOX_time_series_diags = beatboxtestbed._console:plotTimeSeries'
              ]
            },
      include_package_data=True,
      zip_safe=False)
