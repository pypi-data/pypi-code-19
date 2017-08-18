import logging

class BaseManager(object):
    def __init__(self, log_file=''):
        self.logger = logging.getLogger('broker-packager')
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        if log_file:
            hdlr = logging.FileHandler(log_file)
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.WARNING)
    
    def install(self, package, version, git, *args):
        raise NotImplementedError

    def install_list(self, package_list, extra_config={}):
        raise NotImplementedError
    
    def log_install(self, package, *args):
        self.logger.info('Installing {} with args: "{}"'.format(package, ', '.join(map(str, args))))