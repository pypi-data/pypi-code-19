from collections import namedtuple
import logging
import os
from os.path import join, exists, dirname
import threading

from numpy import in1d
import pandas
import pickle
import dill
import keras
from keras.callbacks import EarlyStopping, TensorBoard, TerminateOnNaN
from keras.layers import Input, Embedding, Dense, Reshape, Concatenate, Dropout
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import tensorflow
import xgboost
import lore.io
from lore.encoders import Continuous
import lore.serializers
from lore import env
from lore.callbacks import ReloadBest
from lore.util import timer

logger = logging.getLogger(__name__)


Observations = namedtuple('Observations', 'x y')


class Base(object):
    def __init__(self):
        self.name = join(self.__module__, self.__class__.__name__)
        self.dont_split = None
        self.subsample = None
        self.fitting = None
        self._data_dir = join(env.data_dir, self.name)
        self._data = None
        self._training_data = None
        self._test_data = None
        self._validation_data = None
        self._encoders = None
        self._output_encoder = None
        self._encoded_training_data = None
        self._encoded_validation_data = None
        self._encoded_test_data = None

    def __getstate__(self):
        state = dict(self.__dict__)
        # bloat can be restored via self.__init__() + self.build()
        for bloat in [
            '_data',
            '_training_data',
            '_test_data',
            '_validation_data',
            '_encoded_training_data',
            '_encoded_validation_data'
            '_encoded_test_data',
        ]:
            state[bloat] = None
        return state

    @property
    def training_data(self):
        if self._training_data is None:
            self.cache_data()
        
        return self._training_data
    
    @property
    def validation_data(self):
        if self._validation_data is None:
            self.cache_data()
        
        return self._validation_data
    
    @property
    def test_data(self):
        if self._test_data is None:
            self.cache_data()
        
        return self._test_data
    
    @property
    def encoded_training_data(self):
        if not self._encoded_training_data:
            with timer('encode training data:'):
                self._encoded_training_data = self.encode(self.training_data)
        
        return self._encoded_training_data
    
    @property
    def encoded_validation_data(self):
        if not self._encoded_validation_data:
            with timer('encode validation data:'):
                self._encoded_validation_data = self.encode(self.validation_data)
        
        return self._encoded_validation_data
    
    @property
    def encoded_test_data(self):
        if not self._encoded_test_data:
            with timer('encode test data:'):
                self._encoded_test_data = self.encode(self.test_data)
        
        return self._encoded_test_data

    def encode(self, data):
        self.fit_encoders()
        return Observations(x=self.encode_x(data), y=self.encode_y(data))
    
    def encode_x(self, data):
        x = {}
        for encoder in self._encoders:
            encoded = encoder.transform(data)
            if hasattr(encoder, 'sequence_length'):
                for i in range(encoder.sequence_length):
                    name = encoder.name + '_' + str(i)
                    x[name] = encoded.apply(encoder.get_token, i=i)
            else:
                x[encoder.name] = encoded
        return x

    def encode_y(self, data):
        return self._output_encoder.transform(data)
    
    def decode(self, predictions):
        return self._output_encoder.reverse_transform(predictions)
        
    def fit_encoders(self):
        if not self._encoders:
            with timer('fit encoders:'):
                self._encoders = self.encoders()
                for encoder in self._encoders:
                    encoder.fit(self.training_data)
        if not self._output_encoder:
            with timer('fit output encoder:'):
                self._output_encoder = self.output_encoder()
    
    def cache_data(self):
        if self._data:
            return
        
        path = join(self._data_dir, 'data.pickle')
        if not exists(dirname(path)):
            os.makedirs(dirname(path))
        
        if exists(path):
            with timer('load data from %s:' % path, logging.DEBUG):
                self._data = pandas.read_pickle(path)
        else:
            self._data = self.data()

        if self.subsample:
            logger.debug('subsampling: %s' % self.subsample)
            self._data = self._data.sample(self.subsample)
        
        if not exists(path):
            with timer('save data to %s:' % path, logging.DEBUG):
                self._data.to_pickle(path)

        if self.dont_split:
            train_path = join(self._data_dir, 'train_ids.pickle')
            validate_path = join(self._data_dir, 'validate_ids.pickle')
            test_path = join(self._data_dir, 'test_ids.pickle')
            if exists(train_path) and exists(validate_path) and exists(test_path):
                train_ids = pickle.load(open(train_path, "rb"))
                validate_ids = pickle.load(open(validate_path, "rb"))
                test_ids = pickle.load(open(test_path, "rb"))
            else:
                ids = self._data[self.dont_split].drop_duplicates()
                test_size = len(ids) // 10
                
                train_ids, validate_ids = train_test_split(
                    ids,
                    test_size=test_size,
                    random_state=1
                )
                train_ids, test_ids = train_test_split(
                    train_ids,
                    test_size=test_size,
                    random_state=1
                )
                pickle.dump(train_ids, open(train_path, 'wb'))
                pickle.dump(validate_ids, open(validate_path, 'wb'))
                pickle.dump(test_ids, open(test_path, 'wb'))
            
            rows = self._data[self.dont_split].values
            self._training_data = self._data.iloc[in1d(rows, train_ids.values)]
            self._validation_data = self._data.iloc[in1d(rows, validate_ids.values)]
            self._test_data = self._data.iloc[in1d(rows, test_ids.values)]
        else:
            test_size = len(self._data) // 10
            self._training_data, self._validation_data = train_test_split(
                self._data,
                test_size=test_size,
                random_state=1
            )
            self._training_data, self._test_data = train_test_split(
                self._training_data,
                test_size=test_size,
                random_state=1
            )
            
            
class Keras(Base):
    def __init__(self):
        super(Keras, self).__init__()
        
        self.embed_size = 10
        self.width = 1024
        self.hidden_layers = 4
        self.layer_shrink = 0.5
        self.dropout = 0
        self.batch_size = 32
        self.learning_rate = 0.001
        self.decay = 0.
        self.optimizer = None
        self.keras = None
        self.gain = None
        self.monitor = 'val_acc'
        self.loss = 'categorical_crossentropy'
        
    def __getstate__(self):
        state = super(Keras, self).__getstate__()
        # bloat can be restored via self.__init__() + self.build()
        for bloat in [
            'keras',
            'optimizer',
            '_tf_graph',
            '_tf_graph_lock',
        ]:
            state[bloat] = None
        return state

    @property
    def description(self):
        return '\n'.join([
            '\n  %s' % self.name,
            '==========================================================',
            '| embed | hidden | layer | layer  |         | model      |',
            '| size  | layers | width | shrink | dropout | parameters |',
            '----------------------------------------------------------',
            '| %5i | %6i | %5i | %6.4f | %7.5f | %10i |' % (
                self.embed_size,
                self.hidden_layers,
                self.width,
                self.layer_shrink,
                self.dropout,
                self.keras.count_params()
            ),
            '=========================================================='
        ])
    
    def build(self):
        inputs = self.build_inputs()
        embedding_layer = self.build_embedding_layer(inputs)
        hidden_layers = self.build_hidden_layers(embedding_layer)
        output = self.build_output_layer(hidden_layers)
        
        self.keras = keras.models.Model(inputs=list(inputs.values()), outputs=output)
        self.optimizer = Adam(lr=self.learning_rate, decay=self.decay)
        
        self._tf_graph = tensorflow.get_default_graph()
        self._tf_graph_lock = threading.Lock()

        logger.info('\n\n' + self.description + '\n\n')
    
    def build_inputs(self):
        inputs = {}
        for encoder in self._encoders:
            if hasattr(encoder, 'sequence_length'):
                for i in range(encoder.sequence_length):
                    name = encoder.name + '_' + str(i)
                    inputs[name] = Input(shape=(1,), name=name)
            else:
                inputs[encoder.name] = Input(shape=(1,), name=encoder.name)
        return inputs
    
    def build_embedding_layer(self, inputs):
        embeddings = {}
        reshape = Reshape(target_shape=(self.embed_size,))
        for encoder in self._encoders:
            if isinstance(encoder, Continuous):
                embedding = Dense(self.embed_size, activation='relu')
                embeddings[encoder.name] = embedding(inputs[encoder.name], name='embed_' + encoder.name)
            elif hasattr(encoder, 'sequence_length'):
                for i in range(encoder.sequence_length):
                    name = encoder.name + '_' + str(i)
                    embedding = Embedding(encoder.cardinality(), self.embed_size, name='embed_' + name)
                    embeddings[name] = reshape(embedding(inputs[name]))
            else:
                embedding = Embedding(encoder.cardinality(), self.embed_size, name='embed_' + encoder.name)
                embeddings[encoder.name] = reshape(embedding(inputs[encoder.name]))
        
        return Concatenate()(list(embeddings.values()))
    
    def build_hidden_layers(self, input_layer):
        hidden_layers = input_layer
        
        width = self.width
        for i in range(self.hidden_layers):
            hidden_layers = Dense(int(width), activation='relu', name='hidden_%i' % i)(hidden_layers)
            if self.dropout > 0:
                hidden = Dropout(self.dropout)(hidden)
            if self.layer_shrink < 1:
                width *= self.layer_shrink
            else:
                width -= self.layer_shrink
        
        return hidden_layers
    
    def build_output_layer(self, hidden_layers):
        return Dense(1, activation='sigmoid')(hidden_layers)
    
    @staticmethod
    def last_fitting(self):
        lore.env.models_dir
        
    def fit(self, epochs=100, patience=0, verbose=None, min_delta=0):
        self.fit_encoders()
        self.build()
        self.keras.compile(loss=self.loss, optimizer=self.optimizer)
        if verbose is None:
            verbose = 1 if lore.env.name == lore.env.DEVELOPMENT else 0
        
        logger.info(
            '\n'.join([
                '\n\n\n  Training',
                '==========================================',
                '| benchmark | batch | learning |         |',
                '| loss      | size  | rate     |   decay |',
                '------------------------------------------',
                '| %9.2f | %5i | %8.6f | %7.5f |' % (
                    self.benchmark(),
                    self.batch_size,
                    self.learning_rate,
                    self.decay,
                ),
                '==========================================\n\n'
            ])
        )
        
        serializer = lore.serializers.Keras(model=self)
        serializer.fitting += 1
        reload_best = ReloadBest(
            filepath=serializer.checkpoint_path,
            train=self.encoded_training_data,
            validate=self.encoded_validation_data,
            test=self.encoded_test_data,
            benchmark_loss=self.benchmark(),
            monitor=self.monitor,
            mode='auto',
        )

        self.keras.fit(
            x=self.encoded_training_data.x,
            y=self.encoded_training_data.y,
            validation_data=(self.encoded_validation_data.x, self.encoded_validation_data.y),
            batch_size=self.batch_size,
            epochs=epochs,
            verbose=verbose,
            callbacks=[
                reload_best,
                TerminateOnNaN(),
                EarlyStopping(
                    monitor=self.monitor,
                    min_delta=min_delta,
                    patience=patience,
                    verbose=verbose,
                    mode='auto',
                ),
                # TensorBoard(
                #     log_dir=serializer.tensorboard_path,
                #     histogram_freq=1,
                #     batch_size=self.batch_size,
                #     write_graph=True,
                #     write_grads=True,
                #     write_images=True,
                #     embeddings_freq=1,
                #     embeddings_metadata=None
                # ),
            ]
        )
        
        self.gain = reload_best.gain
        serializer.save(stats=reload_best.stats())
        return reload_best.stats()

    def predict(self, data):
        encoded = self.encode_x(data)
        
        self._tf_graph_lock.acquire()
        try:
            with self._tf_graph.as_default():
                with timer('predict:'):
                    return self.keras.predict(encoded)
            return
        finally:
            self._tf_graph_lock.release()


class XGBoost(Base):
    def __init__(self):
        super(XGBoost, self).__init__()
        self.bst = None
        # http://xgboost.readthedocs.io/en/latest/parameter.html
        self.params = {}
    
    def fit(self):
        self.bst = xgboost.train(
            self.params,
            xgboost.DMatrix(pandas.DataFrame(self.encoded_training_data.x), label=self.encoded_training_data.y),
            num_boost_round=2
        )
        predictions = self.bst.predict(xgboost.DMatrix(pandas.DataFrame(self.encoded_test_data.x)))
        mae = mean_absolute_error(
            predictions,
            self.encoded_test_data.y,
        )
        return {
            'mae': mae
        }

    def predict(self, data):
        encoded = self.encode(data)
        with timer('predict:'):
            prediction = self.bst.predict(encoded)
        return self.decode(prediction)

