"""
http://www.php2python.com/wiki/class.arrayaccess/

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

from objconfig.exception import IndexException


class ArrayAccess():
    """Emulates the ArrayAccess "interface" as a class in Python"""

    def __getitem__(self, key):
        """Get an item from the array."""
        
        raise IndexException("ArrayAccess: __getitem__ not implemented in child class")

    def __setitem__(self, key, value):
        """Set an item in the array."""
        
        raise IndexException("ArrayAccess: __setitem__ not implemented in child class")

    def __delitem__(self, key):
        """Delete an item from th array."""
        
        raise IndexException("ArrayAccess: __delitem__ not implemented in child class")
