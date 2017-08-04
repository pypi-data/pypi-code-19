from setuptools import setup

setup(name='linearcorex',
      version='0.52',
      description='Linear CorEx finds latent factors that explain relationships in data.',
      url='http://github.com/gregversteeg/linearcorex',
      download_url='https://github.com/gregversteeg/linearcorex/archive/0.52.tar.gz',
      author='Greg Ver Steeg',
      author_email='gversteeg@gmail.com',
      license='AGPL-3.0',
      packages=['linearcorex'],
      install_requires=['numpy', 'scipy', 'matplotlib', 'seaborn', 'networkx'])
