from six import python_2_unicode_compatible


@python_2_unicode_compatible
class A(object):
    def __str__(self):
        return 'string from a'


@python_2_unicode_compatible
class B(A):
    def __str__(self):
        return super(B, self).__str__()


a = A()
b = B()
print(str(b))
print(unicode(b))
