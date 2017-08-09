from distutils.core import setup


setup(
  name = 'duckhunt',
  packages = ['duckhunt'], # this must be the same as the name above
  version = '0.1',
  install_requires = ['jsonpickle>=0.9.5'],
  description = 'Library to  frozen class attribute and check types',
  author = 'Vincenzo Marafioti',
  author_email = 'enzo.mar@gmail.com',
  url = 'https://vinmar@bitbucket.org/vinmar/duckhunt.git', # use the URL to the github repo
  keywords = ['bom', 'class', 'setter', 'getter'], # arbitrary keywords
  classifiers = [],
)

