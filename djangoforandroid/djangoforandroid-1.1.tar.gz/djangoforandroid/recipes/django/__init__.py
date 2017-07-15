from djangoforandroid.core.toolchain import PythonRecipe

class DjangoRecipe(PythonRecipe):

    version = '1.11.3'
    url = 'https://github.com/django/django/archive/{version}.tar.gz'
    depends = ['python3crystax']

recipe = DjangoRecipe()
