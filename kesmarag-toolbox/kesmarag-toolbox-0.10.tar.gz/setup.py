from distutils.core import setup

setup(name='kesmarag-toolbox',
      version='0.10',
      description='kesmarag-toolbox',
      author='Costas Smaragdakis',
      author_email='kesmarag@gmail.com',
      packages=['kesmarag', 'kesmarag.ml', 'kesmarag.ua'],
      package_dir={'kesmarag': 'src/kesmarag',
                   'kesmarag.ml': 'src/kesmarag/ml',
                   'kesmarag.ua': 'src/kesmarag/ua'}, )
