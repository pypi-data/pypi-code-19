import os
import stdplus
import yaml

config = {}
configFile = os.path.join(os.path.expanduser("~"),".nephele","config.yaml")

def loadConfig():
    global config
    global configFile
    config={}
    if os.path.exists(configFile):
        print "Loading config:{}".format(configFile)
        config = yaml.load(stdplus.readfile(configFile))
