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


class Countable():
    """Emulates the Countable "interface" as a class in Python"""

    def __len__(self):
        """How many items are in this collection?"""
        
        raise RuntimeException("Countable: __len__ not implemented in child class")

    def count(self):
        """This is the method PHP calls it."""
        
        return self.__len__
