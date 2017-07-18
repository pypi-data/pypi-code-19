import skitai
import sys, os
from .package import mirror, indexer

def bootstrap (pref):	
	config = pref.config
	
	script = None
	if config.get ("enable_mirror", False):
		script = "%s %s %s" % (mirror.__file__, config.remote, config.local)		
	elif config.get ("enable_index", False):
		script = "%s %s" % (indexer__file__, config.resource_dir)
	
	if script:
		logpath = config.get ("logpath")
		redirect = logpath and (" > %s 2>&1" % os.path.join (logpath, "cron.log")) or ""
		skitai.cron (config.sched, r"%s %s%s" % (sys.executable, script, redirect))

