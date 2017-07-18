import os
import wissen
import skitai	

pref = skitai.pref ()
pref.use_reloader = 1
pref.debug = 1

config = pref.config
config.sched = "0/15 * * * *"

config.enable_mirror = False
config.remote = "http://127.0.0.1:5002"
config.local = "http://127.0.0.1:5000"

config.enable_index = False
config.resource_dir = skitai.joinpath ('resources')

config.logpath = os.name == "posix" and '/var/log/assai' or None

skitai.mount ("/v1", (wissen, "app_v1"), "app", pref)
skitai.run (	
	port = 5000,
	logpath = config.logpath
)
