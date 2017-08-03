from distutils.core import setup

setup(name='gecosistema_lite',
      version='0.0.14',
      description='A simple python package',
      author='Valerio Luzzi',
      author_email='valerio.luzzi@gecosistema.it',
      url='https://github.com/valluzzi/libcore/',
      license='MIT',
      packages=['gecosistema_lite'],
      install_requires=['xlrd', 'xlwt', 'xlutils', 'google-api-python-client'],
      python_requires='>=2.7'
      )
