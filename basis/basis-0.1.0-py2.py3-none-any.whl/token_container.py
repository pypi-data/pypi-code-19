#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
file: token_container.py
description: generic vector storage for NLP
author: Luke de Oliveira (lukedeo@vaitech.io)
copyright: 2017 Vai Technologies, LLC. All Rights Reserved.
"""


from abc import ABCMeta, abstractmethod
from collections import Counter
import logging
import os
import pickle
import shutil
import tarfile
import tempfile

import numpy as np

import six

from .utils import pad_sequences

logger = logging.getLogger(__name__)


class TokenContainerException(Exception):
    pass


class UndefinedDimensions(Exception):
    pass


UNK_TOKEN = '<unk>'
PAD_TOKEN = '<pad>'


class TokenContainer(object):
    """
    Box of vectors for a series of elements.

    The box has a size (number of elements) and a vector dimension.
    The box will actually contain the vectors in a matrix W (nb_elements x dim)
    or will implicitly be defined by the number of elements and the vector 
    dimension (this is useful if you don't need to initial values for vectors, 
    or instance for character vector models, which are usually computed via 
    the neural network model).
    """

    __metaclass__ = ABCMeta

    def __init__(self, vocabulary=None, W=None, vector_dim=None,
                 padded=True):
        if vocabulary is not None and not isinstance(vocabulary, list):
            raise TypeError('vocabulary *must* be a list, if passed')

        if vector_dim is not None and not isinstance(vector_dim, int):
            raise TypeError('vector_dim *must* be an int, if passed')

        self._fittable = True
        self._fitted = False

        if W is not None:
            if vocabulary is None:
                raise ValueError('must pass in a vocabulary if passing in an '
                                 'explicit embedding matrix')

            if not len(vocabulary) == W.shape[0]:
                raise ValueError(
                    'dimension mismatch: vocabulary has {} elements, while '
                    'only {} rows of passed in matrix exist.'
                    .format(len(vocabulary), W.shape[0])
                )
            if vector_dim is not None and vector_dim != W.shape[1]:
                logger.warning('specified non-None vector_dim that did not '
                               'match passed-in embedding matrix')
            self._fittable = False

        self._W = W
        self._vocabulary = vocabulary
        self._vector_dim = vector_dim
        self._nn = None

        self.__padded = padded
        self.__pad_integer = None
        self.__offset = 0

        if self.__padded:
            self.__pad_integer = 0
            self.__offset = 1

        if self._vocabulary is not None:
            self._build_token_mapping(self._vocabulary)

    @property
    def W(self):
        return self._W

    @property
    def padding_char(self):
        return self.__pad_integer

    @property
    def padded(self):
        return self.__padded

    @property
    def offset(self):
        return self.__offset

    @property
    def size(self):
        if self._vocabulary is not None:
            return len(self._vocabulary)
        raise UndefinedDimensions('no embedding matrix passed nor any '
                                  'vocabulary constraint')

    @property
    def shape(self):
        if self._W is not None:
            return self._W.shape
        else:
            if self._vocabulary is not None and self._vector_dim is not None:
                return (len(self._vocabulary), self._vector_dim)
            raise UndefinedDimensions('missing information for shape')

    def _get_tok2i(self, tok):
        if tok == PAD_TOKEN:
            return self.__pad_integer
        try:
            return self._tok2i[tok] + self.__offset
        except KeyError:
            return self._tok2i[UNK_TOKEN] + self.__offset

    def _get_i2tok(self, i):
        if not i and self.padded:
            return PAD_TOKEN
        try:
            return self._i2tok[i - self.__offset]
        except KeyError:
            return UNK_TOKEN

    def _build_token_mapping(self, vocabulary):

        self._tok2i = {}
        self._i2tok = {}

        # some word2vec implementations learn a vector for the unk token,
        # some dont
        if UNK_TOKEN not in vocabulary:
            vocabulary += [UNK_TOKEN]

        for idx, tok in enumerate(vocabulary):
            self._i2tok.update({idx: tok})
            self._tok2i.update({tok: idx})

        self._fitted = True

    @abstractmethod
    def _process_iter(self, text_iter, **kwargs):
        pass

    @abstractmethod
    def _process_singleton(self, text, **kwargs):
        pass

    def fit(self, texts, *args, **kwargs):
        if not self._fittable:
            raise TokenContainerException('cannot fit a container on a method '
                                          'initialized from word vectors')
        flow = self._process_iter(texts)

        counts = Counter(token for doc in flow for token in doc)

        self._vocabulary = [v for v, _ in counts.most_common()]
        self._build_token_mapping(self._vocabulary)

    def transform(self, texts, **kwargs):
        if isinstance(texts, six.string_types):
            return self.to_indices(self._process_singleton(texts, **kwargs))
        return self.to_indices(self._process_iter(texts, **kwargs))

    def inverse_transform(self, integer_ids):
        return self.to_tokens(integer_ids)

    def tensor_transform(self, texts, maxlen=None, **kwargs):
        integer_ids = self.transform(texts, **kwargs)
        return np.array(pad_sequences(
            integer_ids, maxlen=maxlen, value=float(self.__pad_integer)
        )).astype('int32')

    def to_embedding(self, vector_dim=None):
        from keras.layers import Embedding

        W = None
        if self.W is not None:
            W = np.zeros((self.size + 1, self.W.shape[1]))
            W[1 if self.padded else 0:-1, :] = self.W
            W = [W]

        emb = Embedding(
            input_dim=self.size + int(self.padded),
            output_dim=self.W.shape[1],
            weights=W,
            mask_zero=self.padded
        )

        return emb

    def to_indices(self, obj):
        if isinstance(obj, six.string_types):
            return self._get_tok2i(obj)
        elif hasattr(obj, '__iter__'):
            return [self.to_indices(o) for o in obj]

    def to_tokens(self, obj):
        if isinstance(obj, int):
            return self._get_i2tok(obj)
        elif hasattr(obj, '__iter__'):
            return [self.to_tokens(o) for o in obj]

    def __getitem__(self, key):
        if self._W is None:
            raise RuntimeError('Vectors have not been added to this index')
        if isinstance(key, six.string_types):
            return self._W[self._get_tok2i(key), :]
        elif hasattr(key, '__iter__'):
            return self._W[list(map(self._get_tok2i, key)), :]

    def save(self, filepath, compressed=False):
        logger.debug('saving with{} compression'
                     .format('' if compressed else 'out'))

        with tarfile.open(filepath, 'w:' + ('gz' if compressed else '')) as ar:
            if self._W is not None:
                with tempfile.NamedTemporaryFile() as tmp:
                    logger.debug('saving npz representation of word vectors')
                    np.save(tmp, self._W, allow_pickle=False)
                    ar.add(tmp.name, 'v')

            attrs_out = ['_tok2i', '_i2tok', '_fitted', 'padded',
                         '_vocabulary', '_vector_dim']

            with tempfile.NamedTemporaryFile() as tmp:
                logger.debug('saving index information')
                pickle.dump({a: getattr(self, a) for a in attrs_out}, tmp)
                ar.add(tmp.name, 'd')

    @classmethod
    def load(cls, filepath):

        tmpdir = tempfile.mkdtemp()

        logger.debug('extracting archive to: {}'.format(tmpdir))

        try:
            with tarfile.open(filepath, 'r:*') as ar:
                ar.extractall(tmpdir)

            meta = pickle.load(open(os.path.join(tmpdir, 'd'), 'rb'))

            instance = cls(padded=meta.pop('padded'))

            for attr_name, attr_val in meta.items():
                setattr(instance, attr_name, attr_val)

            if os.path.exists(os.path.join(tmpdir, 'v')):
                logger.debug('loading word vectors')
                setattr(instance, '_W', np.load(os.path.join(tmpdir, 'v')))
            else:
                logger.debug('no word vectors found in archive')
        except Exception as e:
            logger.error('encountered error: {}'.format(e))
        finally:
            logger.debug('cleaning up {}'.format(tmpdir))
            shutil.rmtree(tmpdir)

        return instance

    @classmethod
    def build_from_file(cls, filepath, padded=False, top_n=None):

        if top_n is not None and not isinstance(top_n, int):
            raise TypeError('top_n must be an integer')

        if not isinstance(filepath, six.string_types):
            raise TypeError('filepath must be a string type')

        with open(filepath, 'r') as buf:

            logger.debug('Loading vectors from {}'.format(filepath))

            vectors = []
            words = []

            # this skips the first line if it has the usual nb_words nb_dim
            # at the top of the file
            if len(buf.readline().split()) != 2:
                buf.seek(0)

            for ctr, line in enumerate(buf):
                if not ctr % 10000:
                    logger.debug('Loading word vector #{}'.format(ctr))

                vals = line.rstrip().split(' ')

                words.append(vals[0])
                vectors.append(list(map(float, vals[1:])))

        logger.debug('converting ingested vectors to embedding matrix')
        W = np.array(vectors[:top_n])

        logger.debug('embedding matrix is {} x {}'.format(*W.shape))

        if padded:
            logger.debug('applying padding token')

        return cls(vocabulary=words[:top_n], W=W[:top_n],
                   vector_dim=W.shape[1], padded=padded)

    def index(self, metric='cosine'):
        if self.W is not None:
            alg = 'brute' if (metric == 'cosine') else 'auto'
            from sklearn.neighbors import NearestNeighbors
            self._nn = NearestNeighbors(metric=metric, algorithm=alg)
            self._nn.fit(self.W)
        else:
            raise TokenContainerException(
                'cannot build similarity on vectorless structure')
        return self

    def nearest(self, token):
        """
        Get nearest words. Word can be a string or an actual word vector.

        >>> gb.nearest('sushi')
        [('sashimi', 0.2923392388266389),
         ('restaurant', 0.45604658750474103),
         ('restaurants', 0.47094956631667273),
         ('chefs', 0.4745822222385485)]
        >>>
        >>> gb.nearest(gb['dad'] - gb['man'] + gb['woman'])
        [('mom', 0.2061153295477789),
         ('dad', 0.23573104771893594),
         ('mother', 0.3477182432927921),
         ('grandmother', 0.35364849686834177),
         ('daughter', 0.42422056933288177)]

        """
        if self._nn is None:
            self.index()

        if isinstance(token, six.string_types):
            query = self.__getitem__(token)
        else:
            # assume that the passed in entity is a vector (np.ndarray)
            query = token

        query = query.reshape((1, -1))
        candidates = zip(*[a.tolist()[0] for a in self._nn.kneighbors(query)])

        return [
            (self.to_tokens(i), d)
            for d, i in candidates if self.to_tokens(i) != token
        ]

    def analogy(self, a, b, c):
        # performs a - b  + c
        v = self.__getitem__(a) - self.__getitem__(b) + self.__getitem__(c)
        v /= np.linalg.norm(v)
        return [(x, y) for x, y in self.nearest(v) if x not in [a, b, c]]
