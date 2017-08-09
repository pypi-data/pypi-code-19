"""Shay Palachy's personal common Python 3 utility functions and classes."""

# flake8: noqa  # prevents 'imported but unused' erros

# pylint: disable=W0614,W0401,C0413
 # pylint: disable=W0611
# import palpyutil.classes as classes
# import palpyutil.collections as collections
# import palpyutil.constants as constants
# import palpyutil.contextmanagers as contextmanagers
import palpyutil.decorators as decorators
# import palpyutil.exceptions as exceptions
# import palpyutil.functions as functions
# import palpyutil.generators as generators
# import palpyutil.math as math
# import palpyutil.functional as functional
# import palpyutil.output as output
# import palpyutil.interface as interface

# cleaning the module's name space
for name in ['get_versions', '_version', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
