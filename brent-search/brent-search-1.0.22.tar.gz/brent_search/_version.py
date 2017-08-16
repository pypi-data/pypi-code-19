# Based on https://stackoverflow.com/q/1462986
# It is used only in the main __init__.py file to lazily inject
# __version__ and version_info variables. This is done to defer the importing
# of pbr and, consequently, pkg_resources therefore speeding up the
# initialization of this package.


class Version(object):
    def __init__(self, name):
        import sys
        self.module = sys.modules[name]
        sys.modules[name] = self
        self.initializing = True

    def __infer_version(self):
        from os.path import basename, dirname, realpath
        from pbr.version import VersionInfo

        pkgname = basename(dirname(realpath(__file__))).replace('_', '-')

        v = VersionInfo(pkgname).semantic_version()

        return v.release_string(), v.version_tuple()

    @property
    def __version__(self):
        return self.__infer_version()[0]

    @property
    def version_info(self):
        return self.__infer_version()[1]

    def __getattr__(self, name):
        # call module.__init__ after import introspection is done
        if self.initializing and not name[:2] == '__' == name[-2:]:
            self.initializing = False
            __init__(self.module)
        return getattr(self.module, name)


def __init__(module):
    pass
