import os
import configparser
import logging

from flickrsync.error import Error
from flickrsync.log import Log
logger = logging.getLogger(Log.NAME)

class Settings:
    CONFIG_DEFAULT = 'DEFAULT'

    def __init__(self, args):
        assert args, "Args not supplied<%s>" % args
        logger.debug('args<%s>' % args)

        configfile = os.path.expanduser('~/.flickrsync/config.ini')
        self.configname = os.path.abspath(args.config if args.config else configfile)

        sectionname = args.profile if args.profile else Settings.CONFIG_DEFAULT
        logger.debug('configname<%s>, sectionname<%s>' % (self.configname, sectionname))

        assert os.path.isfile(self.configname), "Config file not found <%s>" % self.configname

        config = configparser.ConfigParser()
        config.read(self.configname)

        try:
            assert config.get(sectionname, 'api_key'), "api_key not set in config file"
            assert config.get(sectionname, 'api_secret'), "api_secret not set in config file"
            assert config.get(sectionname, 'database') or args.database, "database not set in config file"
            assert config.get(sectionname, 'directory') or args.directory, "directory not set in config file"

            self.api_key = config.get(sectionname, 'api_key')
            self.api_secret = config.get(sectionname, 'api_secret')
            self.username = args.username  if args.username  else config.get(sectionname, 'username')
            self.directory = os.path.abspath(os.path.expanduser(args.directory if args.directory else config.get(sectionname, 'directory')))
            self.database = os.path.abspath(os.path.expanduser(args.database if args.database  else config.get(sectionname, 'database')))

        except configparser.NoOptionError as e:
            raise Error('NoOptionError: configname<%s>, sectionname<%s>, %s' % (self.configname, sectionname, e))
        except configparser.NoSectionError as e:
            raise Error('NoSectionError: configname<%s>, sectionname<%s>, %s' % (self.configname, sectionname, e))

        logger.debug('api_key   <%s>' % self.api_key)
        logger.debug('api_secret<%s>' % self.api_secret)
        logger.debug('username  <%s>' % self.username)
        logger.debug('database  <%s>' % self.database)
        logger.debug('directory <%s>' % self.directory)

        if not os.path.exists(self.directory):
            logger.info("Config file location: <%s>" % self.configname)
            raise Error("picture directory does not exist <%s>" % self.directory)

        if not os.path.exists(os.path.dirname(self.database)):
            os.makedirs(os.path.dirname(self.database), exist_ok=True)
            logger.info("Created database directory <%s>" % os.path.dirname(self.database))

        if not os.path.exists(self.database):
            logger.info("Config file location <%s>" % self.configname)
            logger.info('Database file Does not exist <%s>' % self.database)
