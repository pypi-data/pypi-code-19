import subprocess
from .base import BaseManager

class PyManager(BaseManager):

    def do_install(self, package, pip_paths, *args):
        self.log_install(package, *pip_paths, *args)
        for pip_path in pip_paths:
            subprocess.call([pip_path, 'install', package, *args])

    def install(self, package, version, git, pip_paths=['pip']):
        if package:
            if git:
                self.do_install('git+{}'.format(package), pip_paths)
            elif version:           
                self.do_install('{}=={}'.format(package, version), pip_paths)
            else:
                self.do_install('{}'.format(package), pip_paths, '-U', '--upgrade-strategy', 'only-if-needed')                                        

    def install_list(self, package_list, extra_config={}):
        pip_paths = extra_config.get('pip_paths', ['pip'])
        for package_item in package_list:
            package = package_item.get('name')
            version = package_item.get('version')
            git = package_item.get('git')
            self.install(package, version, git, pip_paths)

