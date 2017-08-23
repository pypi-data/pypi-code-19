from setuptools import setup

setup_defaults = {  
   'name'        : 'fc_hypermesh',
   'description' : 'Generate conforming meshes of any d-orthotopes by simplices or orthotopes with their m-faces',
   'version'     : '0.0.7',
   'url'         : 'http://www.math.univ-paris13.fr/~cuvelier/software',
   'author'      : 'Francois Cuvelier',
   'author_email': 'cuvelier@math.univ-paris13.fr',
   'license'     : 'BSD',
   'packages'    : ['fc_hypermesh'],
   'classifiers':['Topic :: Scientific/Engineering :: Mathematics'],
   } 

setup(name=setup_defaults['name'],
      description = setup_defaults['description'],
      version=setup_defaults['version'],
      url=setup_defaults['url'],
      author=setup_defaults['author'],
      author_email=setup_defaults['author_email'],
      license = setup_defaults['license'],
      packages=setup_defaults['packages'],
      classifiers=setup_defaults['classifiers'],
      install_requires=['fc_tools >= 0.0.13']
     )