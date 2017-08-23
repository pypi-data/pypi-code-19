from setuptools import setup
setup(
  name='bracket_table',
  version='0.1',
  py_modules=['bracket_table'],
  install_requires = ['markdown>=2.5'],
  url='https://github.com/parryc/bracket_table',
  packages=['bracket_table'],
  license='MIT',
  author='parryc',
  author_email='parry@parryc.com',
  keywords='interlinear leipzig glossing gloss markdown',
  classifiers=[
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing :: Filters',
    'Topic :: Text Processing :: Markup :: HTML'
    ]
)