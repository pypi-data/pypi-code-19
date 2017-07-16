from slinkie import Slinkie

template = """
Introduction
------------
This is an implementation of LINQ in Python.

Functions
---------
{functions}

Installation
------------
Slinkie is available on pip, so a simple "pip install slinkie" should do it.
"""


def describe_function(name):
    fn = getattr(Slinkie, name)

    doc = Slinkie(fn.__doc__.splitlines()) \
        .map(str.strip) \
        .filter(lambda it: it != "") \
        .join(' ')

    return f'- {name}: {doc}'


functions = '\n'.join(describe_function(name)
                      for name in dir(Slinkie)
                      if not name.startswith('_'))


with open('README.rst', 'w+') as f:
    data = template.format(functions=functions).strip()
    f.write(data)
