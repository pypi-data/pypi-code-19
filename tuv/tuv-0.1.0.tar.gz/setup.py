import os
from setuptools import setup

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

install_requires = [ 'numpy' ]

if os.path.exists(os.path.join(os.path.dirname(__file__), 'tuv/db.py')):
    install_requires = [ 'numpy', 'scipy' ]

setup(name='tuv',
      description='TUV photolysis rates module for ``boxmox``',
      long_description=read('README.rst') + '\n\n' + read('INSTALL.rst') + '\n\n' + read('CHANGES.rst'),
      version='0.1.0',
      url='https://boxmodeling.meteo.physik.uni-muenchen.de',
      author='Christoph Knote',
      author_email='christoph.knote@physik.uni-muenchen.de',
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
      packages=['tuv'],
      install_requires=install_requires,
      include_package_data=True,
      zip_safe=False)
