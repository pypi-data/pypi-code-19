# exguard - Guard code against exceptions, e.g. for running untrusted module code in a framework
# Copyright (C) 2017  Eike Tim Jesinghaus <eike@naturalnet.de>
# Copyright (C) 2017  Dominik George <nik@naturalnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import inspect
import traceback

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

def traceback_str(excp):
    """ Get the full traceback message as a string.

    :param excp: The exception object.
    :type excp: Exception
    """

    return "".join(traceback.format_exception(excp.__class__, excp, excp.__traceback__))
