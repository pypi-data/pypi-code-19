#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from superkwargs import exceptions
    from superkwargs.inject import inject_kwargs, restore_function
    from superkwargs.decorator import kwarg
    from superkwargs.decorator import superkwarg
except ImportError:
    import exceptions
    from inject import inject_kwargs, restore_function    
    from decorator import kwarg
    from decorator import superkwarg