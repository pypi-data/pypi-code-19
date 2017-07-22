import logging

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

class Cache(Singleton, object):
    '''
    cache dict: key (cache) -> {'value': cached_value, another system info}
    '''
    def __init__(self):
        logger.info('Cache singleton is initialized: {}'.format(id(self)))
        if 'cache' not in self.__dict__:
            self.cache = {}
            logger.info('Cache resetted: {}'.format(id(self.cache)))

    def get(self, key):
        '''
            Returns pair (status, value).
            Status: bool. Is true, if key is stored
        '''
        logger.info('Cahce size: {}'.format(len(self.cache)))
        logger.info('Cache: {}'.format(self.cache))

        if key in self.cache:
            return (True, self.cache.get(key).get('value'))
        else:
            return (False, None)

    def add(self, key, value):
        logging.info('Cache add')
        self.cache[key] = {
            'value': value
        }

