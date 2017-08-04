"""
IGNORE:
    Author: Asher Wolfstein Copyright 2017
    Blog: http://wunk.me/
    E-Mail: asherwunk@gmail.com
    Twitter: https://twitter.com/asherwolfstein Send Me Some Love!
    Package Homepage: http://wunk.me/programming-projects/objconfig-python/
    GitHub: http://github.com/asherwunk/objconfig for the source repository
    DevPost: https://devpost.com/software/objconfig
    Buy Me A Coffee: https://ko-fi.com/A18224XC
    Support Me On Patreon: https://www.patreon.com/asherwolfstein
IGNORE
"""

from objconfig.exception.runtimeexception import RuntimeException


class Iterator():
    """Emulates the Iterator "interface" as a class in Python"""

    def __iter__(self):
        """In PHP iterators support a multitude of functions, to do so in Python only
        requires two overloaders
        
        This returns an iterator object
        """
        
        raise RuntimeException("Iterator: __iter__ not implemented in child class")

    def __next__(self):
        """In PHP iterators support a multitude of functions, to do so in Python only
        requires two overloaders
        
        This is what Python looks for internally
        """
        
        raise RuntimeException("Iterator: __next__ not implemented in child class")
