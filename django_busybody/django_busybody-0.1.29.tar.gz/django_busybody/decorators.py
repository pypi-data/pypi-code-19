# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def _wrap_instance__resolve(wrapping_functions, instance):
    if not hasattr(instance, 'resolve'):
        return instance
    resolve = getattr(instance, 'resolve')

    def _wrap_func_in_returned_resolver_match(*args, **kwargs):
        rslt = resolve(*args, **kwargs)
        if not hasattr(rslt, 'func'):
            return rslt
        f = getattr(rslt, 'func')
        for _f in reversed(wrapping_functions):
            # @decorate the function from inner to outter
            f = _f(f)
        setattr(rslt, 'func', f)
        return rslt
    setattr(instance, 'resolve', _wrap_func_in_returned_resolver_match)
    return instance


def required(wrapping_functions, patterns_rslt):
    '''
    USAGE:

    from django.contrib.auth.decorators import login_required
    from django.contrib.admin.views.decorators import staff_member_required

    mypage_patterns = required(
        login_required,
        [
            ... url patterns ...
        ]
    )

    staff_patterns = required(
        staff_member_required,
        [
            ... url patterns ...
        ]
    )

    urlpatterns += [
        url(r'^staff/', include(staff_patterns, namespace='staff')),
        url(r'^mypage/', include(mypage_patterns, namespace='mypage')),
    ]
    '''
    if not hasattr(wrapping_functions, '__iter__'):
        wrapping_functions = (wrapping_functions,)
    return [
        _wrap_instance__resolve(wrapping_functions, instance)
        for instance in patterns_rslt
    ]
