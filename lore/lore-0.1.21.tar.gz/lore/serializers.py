import pickle
import tensorflow
import os
from os.path import join
import h5py
import sys
import threading

import lore
from lore import encoders, io
from lore.util import timer


class Base(object):
    def __init__(self, klass=None, model=None):
        if model is not None:
            self.path = join(
                lore.env.models_dir,
                model.__module__,
                model.__class__.__name__
            )
        elif klass is not None:
            self.path = join(lore.env.models_dir, klass.__module__, klass.__name__)
        else:
            raise ValueError('You must pass name or model')
        
        self.model = model
        self.model_path = join(self.path, 'model.pickle')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def save(self):
        with timer('pickle model:'):
            pickle.dump(self.model, open(self.model_path, 'wb'))

    def load(self):
        with timer('unpickle model:'):
            self.model = pickle.load(open(self.model_path, 'rb'))

    def upload(self):
        self.save()
        io.upload(self.model_path)

    def download(self):
        io.download(self.model_path)
        return self.load()


class Keras(Base):
    def __init__(self, klass=None, model=None):
        super(Keras, self).__init__(klass=klass, model=model)
        self.weights_path = join(self.path, 'weights.h5')
        self.checkpoint_path = join(self.path, 'checkpoints/{epoch}.h5')
        if not os.path.exists(os.path.dirname(self.checkpoint_path)):
            os.makedirs(os.path.dirname(self.checkpoint_path))

    def save(self):
        super(Keras, self).save()
        
        with timer('save weights:'):
            # Only save weights, because saving named layers that have shared
            # weights causes an error on reload
            self.model.keras.save_weights(self.weights_path)

        # Patch for keras 2 models saved with optimizer weights:
        # https://github.com/gagnonlg/explore-ml/commit/c05b01076c7eb99dae6a480a05ac14765ef08e4b
        with h5py.File(self.weights_path, 'a') as f:
            if 'optimizer_weights' in f.keys():
                del f['optimizer_weights']
        
    def load(self):
        super(Keras, self).load()
        # Rely on build + load_weights rather than loading the named layers
        # w/ Keras because it causes a deserialization issue:
        # Still broken as of Keras 2.0.4
        # https://github.com/fchollet/keras/issues/5442
        self.model.build()
        with timer('load weights:'):
            self.model.keras.load_weights(self.weights_path)
        self.model.tf_graph = tensorflow.get_default_graph()
        self.model.tf_graph_lock = threading.Lock()
        return self.model

    def upload(self):
        super(Keras, self).upload()
        io.upload(self.weights_path)

    def download(self):
        io.download(self.weights_path)
        super(Keras, self).download()


class XGBoost(Base):
    pass
