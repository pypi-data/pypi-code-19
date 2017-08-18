import os
import sys
import platform


MINIMUM_PYTHON_VERSION = (2,7)


class InstallerConfiguration(object):
    """
    A simple class that encapsulates all of the necessary wiring for working out paths,
    compilation flags and other details for setting up ESig.
    """
    def __init__(self, setup_location):
        """
        Constructor for the class.
        """
        self.__package_abs_root = os.path.dirname(setup_location)
    
    
    @property
    def is_x64(self):
        """
        Returns a boolean indicating whether the current system configuration is 64-bit.
        Solution obtained from Python documentation at https://docs.python.org/2/library/platform.html#platform.architecture
        """
        return sys.maxsize > 2 ** 32
    
    
    @property
    def is_windows(self):
        """
        Returns a boolean indicating whether the system is running Windows.
        True is returned if Windows is running, False otherwise.
        """
        return platform.system().lower() == 'windows'
    
    @property
    def compiler_name(self):
        """
        If running Windows, returns a string denoting the version of the Microsoft Visual C++ compiler to use for
        compiling libalgebra. If another platform is running, None is returned.
        """
        if self.is_windows:
            py_major = sys.version_info.major
            py_minor = sys.version_info.minor
        
            if py_major < 3 or (py_major == 3 and py_minor < 3):
                return 'msvc-9.0'
            else:
                if py_major == 3 and py_minor < 5:
                    return 'msvc-10.0'
                else:
                    return 'msvc-14.0'
        
        return None  # Not running Windows; returns None.
    
    
    @property
    def library_dirs(self):
        """
        
        """
        library_paths = []
        
        if self.is_windows:
            boost_path = ''
            instruction_set = 'x64' if self.is_x64 else 'win32'
            compiler_version = 'lib64' if self.is_x64 else 'lib32'
            compiler_version = '{0}-{1}'.format(compiler_version, self.compiler_name)
            
            if 'BOOST_ROOT' in os.environ:
                boost_path = os.environ['BOOST_ROOT']
            
            library_paths.append(os.path.join(boost_path, compiler_version))
            library_paths.append(os.path.join(os.path.join(boost_path,instruction_set),'lib'))
        
        return library_paths
    
    
    @property
    def include_dirs(self):
        """
        numpy is added later on.
        """
        include_dirs = [os.path.join(sys.exec_prefix, 'include')]
        
        if self.is_windows:
            include_dirs.append('.\\src\\')
            include_dirs.append('C:\\libs\\boost_1_63_0\\')
        else:
            include_dirs.append('./src/')
        
        return include_dirs
    
    @property
    def extra_compile_args(self):
        """
        Returns a list of extra compilation options, depending upon the platform specified.
        """
        args = []
        
        if self.is_windows:
            args.append('/EHsc')
            args.append('/DWINVER=0x0601')
            args.append('/D_WIN32_WINNT=0x0601')
            args.append('/D_SCL_SECURE_NO_WARNINGS')
            args.append('/bigobj')
        else:
            args.append('-Wno-unused-but-set-variable')
        
        return args
    
    
    @property
    def linker_args(self):
        """
        Returns a list of args used to be used by the linker when compiling.
        Options are platform-specific.
        """
        args = []
        
        if not self.is_windows:
            args.append('-static')
        
        return args
    
    
    @property
    def boost_libraries(self):
        """
        Returns a list of Boost libraries that are used by libalgebra.
        Note that no libraries are returned if Windows is running - the V C++ compiler should pick the libraries automatically.
        """
        libraries = []
        
        if not self.is_windows:
            libraries.append('boost_system')
            libraries.append('boost_thread')
        
        return libraries
    
    
    def check_python_version(self):
        """
        Runs a simple test -- is the version of Python running the installer acceptable?
        If not, bomb out with a message.
        The minimum version is obtained from the tuple MINIMUM_PYTHON_VERSION.
        """
        if sys.version_info < MINIMUM_PYTHON_VERSION:
            sys.exit("Python 2.7.x or greater is required for esig. Consider upgrading your Python environment.")
    

    def get_version(self):
        """
        Returns a string representing the version number of ESig.
        The version is extracted from the VERSION file, found in the base of the package.
        """
        version_path = os.path.join(self.__package_abs_root, 'VERSION')
        
        with open(version_path, 'r', encoding='utf-8') as version_file:
            version = (version_file.read().strip()).replace(' ', '.')
        
        return version
    
    
    def get_long_description(self):
        """
        Returns a string representing the long description of ESig.
        This is extracted from the README.md file in the base of the package.
        """
        readme_path = os.path.join(self.__package_abs_root, 'README.md')
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            long_description = f.read()
        
        return long_description