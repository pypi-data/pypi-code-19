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


# TODO remove backards compatability hack
sys.modules['encoders'] = encoders

class Keras(object):
    def __init__(self, name=None, model=None):
        if name is None and model is not None:
            self.path = join(
                lore.env.models_dir,
                model.__module__.split('.')[-1],
                model.__class__.__name__
            )
        elif name is not None:
            self.path = join(lore.env.models_dir, name.replace('.', '/'))
        else:
            raise ValueError('You must pass name or model')
        
        self.model = model
        self.model_path = join(self.path, 'model.pickle')
        self.weights_path = join(self.path, 'weights.h5')
        self.checkpoint_path = join(self.path, 'checkpoints/{epoch}.h5')
        if not os.path.exists(os.path.dirname(self.checkpoint_path)):
            os.makedirs(os.path.dirname(self.checkpoint_path))

    def save(self):
        with timer('save model:'):
            pickle.dump(self.model, open(self.model_path, 'wb'))
            # Only save weights, because saving named layers that have shared
            # weights causes an error on reload
            self.model.keras.save_weights(self.weights_path)

        # Patch for keras 2 models saved with optimizer weights:
        # https://github.com/gagnonlg/explore-ml/commit/c05b01076c7eb99dae6a480a05ac14765ef08e4b
        with h5py.File(self.weights_path, 'a') as f:
            if 'optimizer_weights' in f.keys():
                del f['optimizer_weights']
        
    def load(self):
        with timer('load model:'):
            self.model = pickle.load(open(self.model_path, 'rb'))
            # Rely on build + load_weights rather than loading the named layers
            # w/ Keras because it causes a deserialization issue:
            # Still broken as of Keras 2.0.4
            # https://github.com/fchollet/keras/issues/5442
            self.model.build()
            self.model.keras.load_weights(self.weights_path)
            self.model.tf_graph = tensorflow.get_default_graph()
            self.model.tf_graph_lock = threading.Lock()
        return self.model

    def upload(self):
        self.save()
        io.upload(self.model_path)
        io.upload(self.weights_path)

    def download(self):
        io.download(self.model_path)
        io.download(self.weights_path)
        return self.load()
