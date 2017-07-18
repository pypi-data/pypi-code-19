"""Python hook that minimizes disk stats.

The primary interface is to use the `install` function to get the
import hook configured. Ideally that is placed in early startup or
`sitecustomize`.

"""

import imp
import errno
import logging
import marshal
import os
import pkgutil
import re
import sys

__all__ = ["install", "uninstall"]
_log = None
_os_listdir = None
_os_isdir = None
_os_access = None


def install():
    """Install and register the blister import hook.

    It is safe for this to be called multiple times.
    This will place the `_BlisterImp` class on `sys.path_hooks`
    and also replace any existing cached import paths that can
    use the hook.

    """
    if _BlisterImp in sys.path_hooks:
        return

    # Mockfs interferes with loading modules from an install hook
    # So this is required for any testing code that lazily imports
    global _os_listdir, _os_access, _os_isdir
    _os_listdir = os.listdir
    _os_access = os.access
    _os_isdir = os.path.isdir

    global _log
    if _log is None:
        _log = logging.getLogger("blister")
    _log.info("Installing blister import hook")
    sys.path_hooks.append(_BlisterImp)
    for path, value in sys.path_importer_cache.items():
        if value is None:
            try:
                sys.path_importer_cache[path] = _BlisterImp(path)
            except ImportError as err:
                pass


def uninstall():
    """Remove and uninstall the blister import hook.

    It is safe to call this multiple times.
    This remove the `_BlisterImp` class from `sys.path_hooks` and
    any paths cached to use the class are replaced with `None` which
    falls back to a regular Python import.

    """
    try:
        sys.path_hooks.remove(_BlisterImp)
    except ValueError:
        return

    global _log
    if _log is None:
        _log = logging.getLogger("blister")
    _log.info("Uninstalling blister import hook")
    for path, value in sys.path_importer_cache.items():
        if isinstance(value, _BlisterImp):
            sys.path_importer_cache[path] = None


class _BlisterImp(pkgutil.ImpImporter):
    """Internal import hook class for sys.path_hook"""
    _recurse = 0
    _cache = {}
    _suffixes = None
    _volatile = []
    _retoken = None

    def __init__(self, path):
        """Create new path importer hook, raise ImportError if bad path"""
        pkgutil.ImpImporter.__init__(self, path)

        if _BlisterImp._suffixes is None:
            _BlisterImp._suffixes = imp.get_suffixes()

        try:
            self._scan_modules(path)
        except (IOError, OSError) as err:
            raise ImportError(str(err))
        self.__load_data = {}
        self.__path = path


    def find_module(self, fullname, path=None):
        moduleParent, moduleSep, moduleName = fullname.rpartition(".")
        if not moduleName:
            moduleName = moduleParent

        modules = self._scan_modules(self.__path)
        importData = modules.get(moduleName)
        if not importData:
            return None

        # Ensure directory is really a package
        path, suffix = importData
        if suffix[2] == imp.PKG_DIRECTORY:
            pkgNames = self._scan_modules(path)
            if "__init__" not in pkgNames:
                return None

        if not _os_access(path, os.R_OK):
            # Python importer skips unreadable files
            return None

        self.__load_data[fullname] = importData
        return self


    def load_module(self, fullname):
        # PEP-302 claims an existing value in sys.modules must be returned
        # or reload will not work. In practice, the opposite is true.

        # Use try/finally to figure out when first entry completes
        _BlisterImp._recurse += 1
        try:
            import_data = self.__load_data.pop(fullname)
            path, suffix = import_data
            import_file = None
            if suffix[1]:
                try:
                    import_file = open(path, suffix[1])
                except (IOError, OSError) as err:
                    raise ImportError(err.message)
            try:
                mod = imp.load_module(fullname, import_file, path, suffix)
            finally:
                if import_file:
                    import_file.close()

            # Do not put __loader__ into the module because is a real file
            return mod

        finally:
            _BlisterImp._recurse -= 1
            if not _BlisterImp._recurse:
                _BlisterImp._clear_cache()


    def iter_modules(self, prefix=''):
        modules = self._scan_modules(self.__path)
        for name, entry in sorted(modules.iteritems()):
            if name == "__init__":
                continue
            pkg = (entry[1][2] == imp.PKG_DIRECTORY)
            if pkg and "__init__" not in self._scan_modules(entry[0]):
                continue
            yield prefix + name, pkg


    def is_package(self, fullname):
        self.find_module(fullname)
        import_data = self.__load_data.pop(fullname, None)
        if import_data is None:
            raise ImportError("Module was not found '{0}'".format(fullname))
        path, suffix = import_data
        return suffix[2] == imp.PKG_DIRECTORY


    def get_filename(self, fullname):
        # Used by runpy to set __file__
        self.find_module(fullname)
        import_data = self.__load_data.pop(fullname, None)
        if import_data is None:
            raise ImportError("Module was not found '{0}'".format(fullname))
        path, suffix = import_data
        return path


    def get_code(self, fullname):
        self.find_module(fullname)
        import_data = self.__load_data.pop(fullname, None)
        if import_data is None:
            raise ImportError("Module was not found '{0}'".format(fullname))
        path, suffix = import_data
        if suffix[2] == imp.PY_COMPILED:
            try:
                with open(path, suffix[1]) as import_file:
                    import_file.read(8)
                    code = marshal.load(import_file)
            except (IOError, OSError):
                return None
            return code
        if suffix[2] == imp.PY_SOURCE:
            try:
                with open(path, suffix[1]) as import_file:
                    source = import_file.read()
            except (IOError, OSError):
                return None
            return compile(source, path, "exec")
        return None


    def get_source(self, fullname):
        self.find_module(fullname)
        import_data = self.__load_data.pop(fullname, None)
        if import_data is None:
            raise ImportError("Module was not found '{0}'".format(fullname))
        path, suffix = import_data
        if suffix[2] == imp.PY_SOURCE:
            try:
                with open(path, suffix[1]) as import_file:
                    source = import_file.read()
            except (IOError, OSError):
                return None
            return source
        return None


    @staticmethod
    def _scan_modules(path):
        """Get loadable module info from directory, cached if possible"""
        if path == "":
            path = "."

        modules = _BlisterImp._cache.get(path)
        if modules is not None:
            return modules

        _log.debug("Scanning path '%s'", path)
        if not os.path.isabs(path) or _os_access(path, os.W_OK):
            # Relative and writeable directories are volatile and short cached
            _BlisterImp._volatile.append(path)

        if _BlisterImp._retoken is None:
            _BlisterImp._retoken = re.compile(r"^[A-Za-z_]\w*$")

        try:
            dir_list = _os_listdir(path)
        except OSError, err:
            if err.errno in (errno.ENOENT, errno.EIO, errno.EACCES):
                # Unable to read, treated as empty
                dir_list = []
            else:
                # Must raise exception if passed non directory things
                # Which happens when script comes from commandline and python
                # is hunting for a possible __main__.py
                raise

        # Detect packages and group modules by matching suffix
        modules = {}
        suffix_files = dict((s[0], []) for s in _BlisterImp._suffixes)
        pkg_suffix = ("", "", imp.PKG_DIRECTORY)
        for file_name in dir_list:
            file_path = os.path.join(path, file_name)
            if re.match(_BlisterImp._retoken, file_name) and _os_isdir(file_path):
                modules[file_name] = (file_path, pkg_suffix)
            else:
                for suffix in _BlisterImp._suffixes:
                    ext = suffix[0]
                    if file_name != ext and file_name.endswith(ext):
                        mod_name = file_name[:-len(ext)]
                        suffix_files[ext].append((mod_name, file_path))

        # Pick files based on suffix
        for suffix in _BlisterImp._suffixes:
            for mod_name, file_path in suffix_files[suffix[0]]:
                previous = modules.get(mod_name)
                if previous:
                    if previous[1][2] != imp.PKG_DIRECTORY:
                        continue
                if _os_isdir(file_path):
                    continue
                if previous:
                    sub_modules = _BlisterImp._scan_modules(previous[0])
                    if "__init__" in sub_modules:
                        continue
                modules[mod_name] = (file_path, suffix)
        _BlisterImp._cache[path] = modules
        return modules


    @staticmethod
    def _clear_cache():
        """Directories that could change are not cached for long"""
        for path in _BlisterImp._volatile:
            _log.debug("Uncache path '%s'", path)
            _BlisterImp._cache.pop(path, None)
        del _BlisterImp._volatile[:]
