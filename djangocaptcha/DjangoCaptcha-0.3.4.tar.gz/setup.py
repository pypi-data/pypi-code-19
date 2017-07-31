#encoding:utf-8
from distutils.core import setup  
setup(name='DjangoCaptcha',  
      author='TY',  
      author_email='master@t-y.me', 
      version='0.3.4', 
      description='A Captcha module for Django. Py3 supported',
      keywords ='django,captcha',
      url='http://github.com/ty-me/DjangoCaptcha',  
      packages=['DjangoCaptcha'],  
      install_requires=['six', 'pillow'],
      package_data={'DjangoCaptcha':['*.*','DjangoCaptcha/*.*']},

)  
