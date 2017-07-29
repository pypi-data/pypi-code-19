# exguard - Guard code against exceptions, e.g. for running untrusted module code in a framework
# Copyright (C) 2017  Eike Tim Jesinghaus <eike@naturalnet.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version, with the Game Cartridge Exception.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect

def guard(func, exceptions=Exception, modules=[], cb_except=lambda excp, modname: None, cb_finally=lambda excp, modname: None, submodules=False, fullstack=False):
    """ Decorator to guard functions from exceptions.

    :param exceptions: Exceptions the decorated function shall be guarded from
    :type exceptions: list

    :param modules: Modules the module the exception was thrown in shall be compared to
    :type modules: list

    :param cb_except: Function to be run when the decorated function was guarded from an exception. This function needs to take the exception as an argument.
    :type cb_except: function

    :param cb_finally: Function to be run after everything, regardless of an exception being thrown or catched or not existing. This function needs to take the exception as an argument.
    :type cb_finally: function

    :param submodules: Determines whether submodules of the modules given should be checked too.
    :type submodules: bool

    :param fullstack: Determines whether it's indifferent where in the stack the exception was caught.
    :type fullstack: bool

    :rtype: function
    """

    # Change module objects to their string names
    modules = [mod if isinstance(mod, str) else mod.__name__ for mod in modules]

    # Define new (decorated) function
    def guarded_func(*args, **kwargs):
        # Default the thrown exception to None
        thrown = (None, None)
        # Try to run the function with given arguments
        try:
            return func(*args, **kwargs)
        # If there was an exception specified in exceptions, catch it
        except exceptions as excp:
            # Get the stack
            stack = inspect.trace()

            # Iterate over all frames if fullstack is True, if not only check for the last frame
            for frm in stack[(0 if fullstack else -1):]:
                # Get the name of the module the expcetion came from
                modname = inspect.getmodule(frm[0]).__name__

                # Check whether the exception came from a module specified in modules or a submodule of those if submodules is True
                if not modules or modname in modules or (submodules and bool(list(filter(lambda mod: ("%s." % modname).startswith("%s." % mod), modules)))):
                    # Set thrown to correct exception to use in finally-block later
                    thrown = (excp, modname)
                    break

            if thrown[0]:
                # If so, run cb_except
                cb_except(*thrown)
            else:
                # If not, raise the exception as usual
                raise
        # After everything
        finally:
            # Run cb_finally on the thrown exception
            cb_finally(*thrown)

    # Return the decorated function
    return guarded_func
