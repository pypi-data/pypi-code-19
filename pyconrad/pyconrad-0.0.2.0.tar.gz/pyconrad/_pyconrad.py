
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

from jpype import startJVM, shutdownJVM, getDefaultJVMPath, isJVMStarted, JPackage, java
from jpype import attachThreadToJVM, detachThreadFromJVM, JException, JProxy, JClass, JDouble, JArray
import threading
import time
import os
from . import _windowlistener as wl
import pyconrad_java
from pathlib import Path
from ._constructorproxies import pointNdConstructor, simpleVectorConstructor

module_path = os.path.dirname(__file__)



class PyConrad:

    #Namespaces
    classes, ij, java = None,None,None

    __conrad_path = None
    __conrad_repo_set = None

    __is_gui_started = None

    __gui_instance = None
    __gui_thread = None
    ___instance = None

    __imported_namespaces = []


    def __new__(cls, *args, **kwargs):
        if not cls.___instance:
            cls.___instance = super(PyConrad, cls).__new__(
                cls, *args, **kwargs)
        return cls.___instance


    @staticmethod
    def get_instance():
        if PyConrad.___instance is None:
            PyConrad.___instance = PyConrad()
        return PyConrad.___instance

    def setup(self, max_ram = '8G', min_ram = '7G', dev_dirs = []):
        if not self.is_java_initalized():
            try:
                curr_directory = os.getcwd()
                conrad_source_and_libs = self.__import__libs(dev_dirs)
                os.chdir(self.__conrad_path)
                startJVM(getDefaultJVMPath(), conrad_source_and_libs, "-Xmx%s" % max_ram, "-Xmn%s" % min_ram )
                os.chdir(curr_directory)
                self.classes = JPackage('edu')
                self.ij = JPackage('ij')
                self.java = java
            except JException as ex:
                print(ex)
        else:
            print("JVM already started")

    def start_conrad(self):
        if self.__gui_thread is None:
            self.__gui_thread = threading.Thread(target=self.__start_ij_gui)
            self.__gui_thread.start()
            while not self.__is_gui_started:
                time.sleep(1)
        else:
            print("Some GUI is already started")

    def start_reconstruction_filter_pipeline(self):
        if self.__gui_thread is None:
            self.__gui_thread = threading.Thread(target=self.__start_rfp_gui)
            self.__gui_thread.start()
            while not self.__is_gui_started:
                time.sleep(1)
        else:
            print("Some GUI is already started")

    def is_java_initalized(self):
        return isJVMStarted()

    def __stop_gui(self):
        java.lang.System.exit(0)
        self.__is_gui_started = False

    def __start_rfp_gui(self):
        attachThreadToJVM()
        self.__gui_instance = JPackage("edu").stanford.rsl.apps.gui
        listener = wl.WindowListener()
        proxy = JProxy("java.awt.event.WindowListener", inst=listener)
        self.__gui_instance.ReconstructionPipelineFrame.startConrad(proxy)
        self.__is_gui_started = True
        print('Gui started', self.__gui_instance)
        detachThreadFromJVM()
        while self.__is_gui_started:
            time.sleep(1)

    def __start_ij_gui(self):
        attachThreadToJVM()
        self.__gui_instance = JPackage("edu").stanford.rsl.conrad.utils
        listener = wl.WindowListener()
        proxy = JProxy("java.awt.event.WindowListener", inst=listener)
        self.__gui_instance.CONRAD.setup(proxy)
        self.__is_gui_started = True
        print('Gui started', self.__gui_instance)
        detachThreadFromJVM()
        while self.__is_gui_started:
            time.sleep(1)

    def __import__libs(self, dev_dirs):
        # if user forgets the brackets
        if isinstance(dev_dirs, str):
            dev_dirs = [dev_dirs]

        # check whether CONRAD + RSL can be found nearby
        # yes: navigate there
        # no: use conrad.jar
        # list directories, check whether CONRAD/RSL are there
        self.conrad_repo_set = False

        extra_libs = ''
        dev_src = []
        for dev in dev_dirs:
            dev_path = Path(dev)
            dev_src.append(dev_path.joinpath('src'))
            if dev_path.match("CONRAD"):
                self.__conrad_path = dev_path
                self.__conrad_repo_set = True
                dev_lib = dev_path.joinpath('lib')
                dev_classes = dev_path.joinpath('classes', 'production', 'CONRAD')
                os.chdir(dev_path)
                extra_libs = (dev_lib.joinpath(fn) for fn in dev_lib.iterdir() if '.jar' == fn.suffix)
                extra_libs = ';'.join(map(str, [dev_classes, *extra_libs]))

        if self.__conrad_repo_set:
            src = ';'.join(map(str, dev_src))
            s = '-Djava.class.path=%s;%s' % (src, extra_libs)
        else:
            self.__conrad_path = pyconrad_java.conrad_jar_dir
            dev_src.append(pyconrad_java.conrad_jar_path)
            src = ';'.join(map(str, dev_src))
            s = '-Djava.class.path=%s;%s' % (src, extra_libs)

        #Unix-like systems use : instead of ; to separate classpaths
        if os.name != 'nt':  # Windows
            s = s.replace(';',':')
        return s

    def terminate(self):
        if self.is_gui_started():
            self.__stop_gui()
        shutdownJVM()

    def is_gui_started(self):
        return self.__is_gui_started

    def add_import(self, package_name):
        self.__imported_namespaces.append(package_name)

    def __getitem__(self, classname):
        if(classname == 'PointND'):
            return pointNdConstructor
        if(classname == 'SimpleVector'):
            return simpleVectorConstructor

        success = None

        # Default namespace
        try:
            rtn = JClass(classname)
            success = rtn
        except:
            pass

        # Imported namespaces
        for package in self.__imported_namespaces:
            try:
                rtn = JClass(package + "." + classname)
                success = rtn
                break
            except:
                pass

        if success == None:
            raise Exception('Class \"%s\" not found in the following namespaces:\n %s' % (classname,self.__imported_namespaces))

        return success

    def enumval_from_int(self, enum_name, value_int):
        return self[enum_name].values()[int(value_int)]

    def enumval_from_string(self, enum_name, value_string):
        return self[enum_name].valueOf(value_string)
