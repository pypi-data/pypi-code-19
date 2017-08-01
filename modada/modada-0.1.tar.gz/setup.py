try: 
    from setuptools import setup 
except ImportError: 
    from distutils.core import setup 

config = {
    'description': 'the tiny game about legend of modada',
    'author': 'Aaron',
    'author_email': 'shuju891@163.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['MODADA'],
    'scripts': [],
    'name': 'modada'
}
setup(**config)
