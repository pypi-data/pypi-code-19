from django.core.exceptions import PermissionDenied


def test_perm(user, perm):
    if not user.has_perm(perm):
        raise PermissionDenied
