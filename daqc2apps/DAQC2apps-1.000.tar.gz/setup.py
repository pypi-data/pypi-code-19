from setuptools import setup, find_packages
# from setuptools.command.develop import develop
# from setuptools.command.install import install
import site
import os
import sys
from os.path import expanduser
import atexit
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        def _post_install():
            def find_module_path():
                myname = expanduser("~")
                for p in sys.path:
                    if os.path.isdir(p) and 'piplates' in os.listdir(p):
                        return os.path.join(p, 'piplates')
            install_path = find_module_path()
            # Add your post install code here
            #home = expanduser("~")
            _USERNAME = os.getenv("SUDO_USER") or os.getenv("USER")
            home='/home/'+_USERNAME
            #target=home+'/Applications'
            target=home
            frompath=install_path+'/Applications'
            cmd='cp -r '+frompath+' '+target
            #print(cmd)
            os.system(cmd)     
            frompath=frompath+'/Shortcuts/*.desktop'
            target=home+'/Desktop'
            cmd='cp '+frompath+' '+target
            #print(cmd)
            os.system(cmd)     
        atexit.register(_post_install)
        install.run(self)
        
setup(
    name='DAQC2apps',
    version='1.000',
    license='BSD',
    author='Jerry Wasinger, WallyWare, inc.',
    author_email='support@pi-plates.com',
    keywords = "pi-plates,data acquisition, raspberry pi, relays, motors",
    url='https://www.pi-plates.com',
    long_description="README.txt",
    packages=['piplates','piplates.Applications','piplates.Applications.Assets','piplates.Applications.Shortcuts'],
    include_package_data=True,
    cmdclass={'install': CustomInstall},
    package_data={
    	'' : ['*.txt'],
    	'Applications':['*.ui','*.pdf'],
        'Applications.Assets':['*.png'],
        'Applications.Shortcuts':['*.*'],
    	},
    description="Pi-Plates Application Setup",
)