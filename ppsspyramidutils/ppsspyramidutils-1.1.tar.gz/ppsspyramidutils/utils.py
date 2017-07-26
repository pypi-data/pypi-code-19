import logging
l = logging.getLogger(__name__)

class Utils():
    myconf = []



    @classmethod
    def config(cls,config,prefix=None):
        if not prefix:
            prefix = cls.__name__.lower()
        for k in cls.myconf:
            key = prefix+"."+k
            if key in config:
                l.debug("value of {key}: {val}".format(key=k,val=config[key]))
                setattr(cls,k,unicode(config[key]) ) 