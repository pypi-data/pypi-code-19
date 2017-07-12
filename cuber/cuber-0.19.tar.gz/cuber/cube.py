import abc
import cPickle as pickle
import os.path
import logging

logger = logging.getLogger(__name__)

class Cube(object):
    __metaclass__  = abc.ABCMeta

    checkpoints_dir = 'checkpoints/'

    @abc.abstractmethod
    def name(self):
        '''
            Unique name for cube and params. This name is key for cache.
        '''
        return

    def get(self):
        '''
            Checks if there is a cached verison and loads it.
            If there is no cached version, runs calcualtions via eval function.
            If you want to get cube's result, use only this function.
        '''
        pickle_name = os.path.join(Cube.checkpoints_dir, '{}.pkl'.format(self.name()))
        logger.info('Pickle name: {}'.format(pickle_name))
        if not os.path.isfile(pickle_name):
            logger.info('Cache is not ok. Evaluating...')
            data = self.eval()
            logger.info('Writing cache')
            if not os.path.isdir(Cube.checkpoints_dir):
                os.makedirs(Cube.checkpoints_dir)
            with open(pickle_name, 'wb') as f:
                pickle.dump(data, f)
        else:
            logger.info('Cache is ok')
        logger.info('Loading from cache')
        with open(pickle_name, 'rb') as f:
            data = pickle.load(f)
        logger.info('Loaded')
        return data

    @abc.abstractmethod
    def eval(self):
        '''
            This method should contain meaningful calculations. It have to return dict with result.
        '''
        return
