from setuptools import setup

setup(name='build_scenarist',
      version='0.6.2',
      description='',
      url='http://github.com/sogimu/scenarist',
      author='Aleksandr Lizin',
      author_email='sogimu@nxt.ru',
      license='MIT',
      packages=['build_scenarist'],
      scripts=['scenarist.py'],
      package_data={'build_scenarist': ['src/*']},
      zip_safe=False)
