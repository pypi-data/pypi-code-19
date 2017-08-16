from setuptools import setup, Extension

module = Extension('medioex',
                   sources=['medioex.c'],
                   libraries=['bcm2835'],
                   extra_compile_args=['-std=gnu11', '-lbcm2835'],
                   extra_link_args=['-std=gnu11']
                   )

setup(name='medioex',
      version='0.1.11',
      description='Python MedIOEx module',
      url = 'https://github.com/beyaznet/python-medioex-module',
      author = 'Beyaz R&D Team',
      author_email = 'arge@beyaz.net',
      license = 'GNU GPLv3',
      keywords = 'raspberry pi medioex taliabee',
      python_requires='>=3',
      ext_modules=[module],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: C'
      ]
)
