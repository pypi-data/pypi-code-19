from setuptools import setup
import sys

if sys.version_info[0] > 2:
    install_requires = ['setuptools',
                        'unicodecsv',
                        'regex',
                        'panphon>=0.7',
                        'marisa_trie']
else:
    install_requires = ['setuptools',
                        'unicodecsv',
                        'regex',
                        'subprocess32',
                        'panphon>=0.7',
                        'marisa_trie']

setup(name='epitran',
      version='0.19',
      description='Tools for transcribing languages into IPA.',
      url='http://github.com/dmort27/epitran',
      download_url='http://github.com/dmort27/epitran/tarball/0.19',
      author='David R. Mortensen',
      author_email='dmortens@cs.cmu.edu',
      license='MIT',
      install_requires=install_requires,
      scripts=['epitran/bin/epitranscribe.py',
               'epitran/bin/uigtransliterate.py',
               'epitran/bin/detectcaps.py',
               'epitran/bin/connl2ipaspace.py',
               'epitran/bin/connl2engipaspace.py',
               'epitran/bin/migraterules.py',
               'epitran/bin/decompose.py',
               'epitran/bin/testvectorgen.py',
               'epitran/bin/transltf.py'],
      packages=['epitran'],
      package_dir={'epitran': 'epitran'},
      package_data={'epitran': ['data/*.csv', 'data/*.txt',
                                'data/map/*.csv', 'data/*.json',
                                'data/pre/*.txt', 'data/post/*.txt',
                                'data/space/*.csv', 'data/strip/*.csv',
                                'data/reromanize/*.csv',
                                'data/rules/*.txt']},
      zip_safe=True,
      classifiers=['Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Text Processing :: Linguistic']
      )
