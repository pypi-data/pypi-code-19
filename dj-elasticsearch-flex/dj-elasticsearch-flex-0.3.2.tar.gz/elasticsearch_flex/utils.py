import six
from six.moves import reduce


def rgetattr(obj, attr, allow_null=True):
    attrs = attr.split('__')

    def _get_attr(o, a):
        try:
            return getattr(o, a)
        except AttributeError as e:
            if not allow_null:
                raise e

    return reduce(_get_attr, [obj] + attrs)


def memoized_property(fget):
    """
    Return a property attribute for new-style classes that only calls its getter
    on the first access. The result is stored and on subsequent accesses is
    returned, preventing the need to call the getter any more.

    Example:
    Following classes C, and D are equivalent.
    >>> class C(object):
    ...   @memoized_property
    ...   def name(self):
    ...     return expensive_function_call()
    >>> class D(object):
    ...   @property
    ...   def name(self):
    ...     if not hasattr(self, '_name'):
    ...       self._name = expensive_function_call()
    ...     return self._name
    """
    attr_name = '_{0}'.format(fget.__name__)

    @six.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)
