import logging
import logging.config
import sys

class Logger(object):
    def __init__(self, profile, scriptname):
        """
        The main entry point of the logging
        """
        self.profile = profile
        self.scriptname = scriptname

        ### logfilename
        self.file_name = get_log(profile)
        self.fh = logging.FileHandler(self.file_name)

        self.log = logging.getLogger(scriptname)
        self.log.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh.setFormatter(formatter)
        # add handler to logger object
        self.log.addHandler(self.fh)

        self.log.info("==================================================")
        self.log.info("===* STARTING SCRIPT: {:} *===".format(scriptname))
        self.log.info("Part of project {:} (current user: {:})".format(profile['active'], profile['activeuser']))
        self.log.info("Hosted @ {:} (OS: {:})".format(profile[profile['active']]['systems'], OS))
        self.log.info("Python version: {:}".format(sys.version))

    def close(self):
        logger = logging.getLogger(self.scriptname)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.fh)
        logger.info("===*  ENDING SCRIPT  *===")
        logger.info("==================================================")
