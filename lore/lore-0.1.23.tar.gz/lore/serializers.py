import pickle
import os
from os.path import join
import h5py
import json
import re

import lore
from lore import io
from lore.util import timer


class Base(object):
    def __init__(self, klass=None, model=None):
        self.path = None
        self.fitting_path = None
        self.model_path = None
        self.remote_model_path = None
        self.model = model
        self._fitting = None

        if model is not None:
            self.path = join(lore.env.models_dir, model.__module__, model.__class__.__name__)
        elif klass is not None:
            self.path = join(lore.env.models_dir, klass.__module__, klass.__name__)
        else:
            raise ValueError('You must pass name or model')
        self.fitting = self.last_fitting()

    def last_fitting(self):
        if not os.path.exists(self.path):
            return 1
            
        fittings = [int(d) for d in os.listdir(self.path) if re.match(r'^\d+$', d)]
        if not fittings:
            return 1
        
        return sorted(fittings)[-1]

    @property
    def fitting(self):
        return self._fitting
    
    @fitting.setter
    def fitting(self, value):
        self._fitting = value
        self.fitting_path = join(self.path, str(self._fitting))
        model_file = 'model.pickle'
        self.model_path = join(self.fitting_path, model_file)
        self.remote_model_path = join(self.path, model_file)
        if not os.path.exists(self.fitting_path):
            os.makedirs(self.fitting_path)

    def save(self, stats=None):
        with timer('pickle model:'):
            pickle.dump(self.model, open(self.model_path, 'wb'))

        with open(join(self.fitting_path, 'params.json'), 'w') as f:
            if hasattr(self.model, 'params'):
                params = self.model.params
            else:
                params = {}
                for key, value in self.model.__getstate__().items():
                    if not key.startswith('_'):
                        params[key] = value.__repr__()
            json.dump(params, f)

        if stats:
            with open(join(self.fitting_path, 'stats.json'), 'w') as f:
                json.dump(stats, f)
        
    def load(self, fitting=None):
        if fitting:
            self.fitting = fitting
        
        with timer('unpickle model:'):
            self.model = pickle.load(open(self.model_path, 'rb'))

    def upload(self):
        self.save()
        io.upload(self.model_path, self.remote_model_path)

    def download(self):
        self.fitting = 0
        io.download(self.model_path, self.remote_model_path)
        return self.load()


class Keras(Base):
    def __init__(self, klass=None, model=None):
        self.weights_path = None
        self.remote_weights_path = None
        self.checkpoint_path = None
        self.tensorboard_path = None
        super(Keras, self).__init__(klass=klass, model=model)

    @Base.fitting.setter
    def fitting(self, value):
        Base.fitting.fset(self, value)  # this is a "pythonic" super() call :(
        weights_file = 'weights.h5'
        self.weights_path = join(self.fitting_path, weights_file)
        self.remote_weights_path = join(self.path, weights_file)
        self.checkpoint_path = join(self.fitting_path, 'checkpoints/{epoch}.h5')
        if not os.path.exists(os.path.dirname(self.checkpoint_path)):
            os.makedirs(os.path.dirname(self.checkpoint_path))
        self.tensorboard_path = join(self.fitting_path, 'tensorboard')
        if not os.path.exists(os.path.dirname(self.tensorboard_path)):
            os.makedirs(os.path.dirname(self.tensorboard_path))

    def save(self, stats=None):
        super(Keras, self).save(stats)
        
        with timer('save weights:'):
            # Only save weights, because saving named layers that have shared
            # weights causes an error on reload
            self.model.keras.save_weights(self.weights_path)

        # Patch for keras 2 models saved with optimizer weights:
        # https://github.com/gagnonlg/explore-ml/commit/c05b01076c7eb99dae6a480a05ac14765ef08e4b
        with h5py.File(self.weights_path, 'a') as f:
            if 'optimizer_weights' in f.keys():
                del f['optimizer_weights']
        
    def load(self, fitting=None):
        super(Keras, self).load(fitting)
        # Rely on build + load_weights rather than loading the named layers
        # w/ Keras for efficiency (and also because it causes a
        # deserialization issue) as of Keras 2.0.4:
        # https://github.com/fchollet/keras/issues/5442
        self.model.build()
        with timer('load weights:'):
            self.model.keras.load_weights(self.weights_path)
        return self.model

    def upload(self):
        super(Keras, self).upload()
        io.upload(self.weights_path, self.remote_weights_path)

    def download(self):
        self.fitting = 0
        io.download(self.weights_path, self.remote_weights_path)
        return super(Keras, self).download()


class XGBoost(Base):
    pass
