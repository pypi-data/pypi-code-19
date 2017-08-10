from setuptools import setup, Extension


sslpsk = Extension(
  'pytlspsk/_ssl_psk',
  sources = ['pytlspsk/ssl_psk.c'],
  libraries = ['ssl'],
)

setup(
  name = 'pytlspsk',
  packages = ['pytlspsk'], # this must be the same as the name above
  version = '0.3',
  description = 'TLS-PSK wrapper for Socket',
  author = 'Jignesh Vasoya',
  author_email = 'jigneshvasoya@gmail.com',
  url = 'https://github.com/jigneshvasoya/pytlspsk', # use the URL to the github repo
  download_url = 'https://github.com/jigneshvasoya/pytlspsk/tarball/0.3', # I'll explain this in a second
  keywords = ['OpenSSL', 'TLS-PSK', 'tlspsk', 'security', 'ssl socket'], # arbitrary keywords
  classifiers = [
      'Development Status :: 2 - Pre-Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Programming Language :: C',
      ],
  package_data = {'pytlspsk': ['_ssl_psk.so']},
  ext_modules = [sslpsk]
)
