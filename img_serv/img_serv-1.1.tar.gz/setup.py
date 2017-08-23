from distutils.core import setup
lib_name = 'img_serv'
setup(
  name = lib_name,
  packages = [lib_name], # this must be the same as the name above
  version = '1.1',
  description = 'Library which helps with sending and receiving images. Developed to help people focus on the image processing more without having to worry about the networking aspects.',
  author = 'Prasanna L S',
  author_email = 'prasanna.pessu@gmail.com',
  url = 'https://github.com/prasannals/ImgServ', # use the URL to the github repo
  download_url = 'https://github.com/prasannals/ImgServ/archive/1.1.tar.gz',
  keywords = ['server', 'client', 'image_processing'], # arbitrary keywords
  classifiers = [],
)
