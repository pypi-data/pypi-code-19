from distutils.core import setup

setup(
    name='djongo',
    version='1.2',
    packages=['djongo'],
    url='https://github.com/nesdis/djongo',
    license='BSD',
    author='nesdis',
    author_email='nesdis@gmail.com',
    description='Driver for allowing Django to use NoSQL databases',
	install_requires=[
          'sqlparse',
		  'pymongo'
      ],
)
