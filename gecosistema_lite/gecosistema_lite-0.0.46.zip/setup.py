from distutils.core import setup

setup(name='gecosistema_lite',
      version='0.0.46',
      description='A simple python package',
      author='Valerio Luzzi',
      author_email='valerio.luzzi@gecosistema.it',
      url='https://github.com/valluzzi/libcore/',
      license='MIT',
      packages=['gecosistema_lite'],
      install_requires=['xlrd', 'xlwt', 'xlutils'],
      python_requires='>=2.7'
      )
