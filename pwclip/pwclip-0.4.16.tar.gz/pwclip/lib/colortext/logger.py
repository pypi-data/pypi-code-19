from os import getuid, makedirs
from os.path import basename, expanduser, isdir
from logging import basicConfig, getLogger, INFO

def logger(name):
	logdir = '/var/log/%s'%name
	if getuid() != 0:
		logdir = expanduser('~/log/%s'%name)
	logfile = '%s/%s.log'%(logdir, name)
	if not isdir(logdir):
		makedirs(logdir)
	basicConfig(
        format='%(asctime)s,%(msecs)03d ' \
            '%(levelname)s %(funcName)s - %(message)s',
        level=INFO, filename=logfile, datefmt='%F.%T')
	return getLogger(logfile)
