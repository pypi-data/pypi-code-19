from os.path import basename, dirname, realpath

from pbr.version import VersionInfo

pkgname = basename(dirname(realpath(__file__))).replace('_', '-')

v = VersionInfo(pkgname).semantic_version()
__version__ = v.release_string()
version_info = v.version_tuple()
