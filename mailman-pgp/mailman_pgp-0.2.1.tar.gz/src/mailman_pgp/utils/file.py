# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

""""""
from functools import wraps

from flufl.lock import Lock


def locked(lockfile, *lock_args, **lock_kwargs):
    """

    :param lockfile:
    :param lock_args:
    :param lock_kwargs:
    :return:
    """

    def locked_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Lock(lockfile, *lock_args, **lock_kwargs):
                return func(*args, **kwargs)

        return wrapper

    return locked_decorator


def locked_obj(lockattr, *lock_args, **lock_kwargs):
    """

    :param lockattr:
    :param lock_args:
    :param lock_kwargs:
    :return:
    """

    def locked_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lockfile = getattr(args[0], lockattr)
            locked_func = locked(lockfile, *lock_args, **lock_kwargs)(func)
            return locked_func(*args, **kwargs)

        return wrapper

    return locked_decorator
