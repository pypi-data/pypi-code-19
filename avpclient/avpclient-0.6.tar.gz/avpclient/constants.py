class _const:
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if "locked" in self.__dict__:
            raise NameError("Class is locked can not add any attributes (%s)" % name)
        if name in self.__dict__:
            raise NameError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

import sys
sys.modules[__name__]=_const()
