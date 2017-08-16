from .managers.python import PyManager
from .managers.r import RManager

class Installer(object):
    def __init__(self, config={}):
        python_log_file = config.get('python', {}).get('log_file', '')
        r_log_file = config.get('r', {}).get('log_file', '')
        self.managers = {'python': PyManager(python_log_file), 'r': RManager(r_log_file)}

    def install(self, config):
        for manager_name in self.managers:
            manager = self.managers[manager_name]
            manager.install_list(config.get(manager_name, {}).get('paths', []), config.get(manager_name, {}))