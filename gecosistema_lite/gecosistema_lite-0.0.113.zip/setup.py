from distutils.core import setup

setup(name='gecosistema_lite',
      version='0.0.113',
      description='A simple python package',
      author='Valerio Luzzi',
      author_email='valerio.luzzi@gecosistema.it',
      url='https://github.com/valluzzi/libcore/',
      license='MIT',
      packages=['gecosistema_lite'],
      install_requires=['pyproj', 'rarfile', 'xlrd', 'xlwt', 'xlutils', 'jinja2', 'xmljson', 'openpyxl'],
      python_requires='>=2.7'
      )
