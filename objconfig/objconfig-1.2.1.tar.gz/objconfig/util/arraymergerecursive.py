"""
PHP 2 Python Function Port

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


# http://www.php2python.com/wiki/function.array-merge-recursive/
def array_merge_recursive(array1, *arrays):
    """Emulates the array_merge_recursive function."""

    for array in arrays:
        for key, value in array.items():
            if key in array1:
                if isinstance(value, dict):
                    array[key] = array_merge_recursive(array1[key], value)
                if isinstance(value, (list, tuple)):
                    array[key] += array1[key]
        array1.update(array)
    return array1
