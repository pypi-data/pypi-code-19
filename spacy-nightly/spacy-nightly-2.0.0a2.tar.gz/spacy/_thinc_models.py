from spacy.attrs import ORTH, LOWER, PREFIX, SUFFIX, SHAPE

from thinc.neural.util import get_array_module
from thinc.neural.optimizers import Adam
from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.api import with_getitem
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.relu import ReLu
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural.util import to_categorical
from thinc.api import FeatureExtracter

from thinc.neural.pooling import Pooling, max_pool, mean_pool
from thinc.neural._classes.difference import Siamese, CauchySimilarity
from thinc.linear.linear import LinearModel

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.resnet import Residual
from thinc.neural._classes.batchnorm import BatchNorm as BN


@layerize
def _flatten_add_lengths(seqs, pad=0, drop=0.):
    ops = Model.ops
    lengths = ops.asarray([len(seq) for seq in seqs], dtype='i')
    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths, pad=pad)
    X = ops.flatten(seqs, pad=pad)
    return (X, lengths), finish_update


@layerize
def _logistic(X, drop=0.):
    xp = get_array_module(X)
    if not isinstance(X, xp.ndarray):
        X = xp.asarray(X)
    # Clip to range (-10, 10)
    X = xp.minimum(X, 10., X)
    X = xp.maximum(X, -10., X)
    Y = 1. / (1. + xp.exp(-X))
    def logistic_bwd(dY, sgd=None):
        dX = dY * (Y * (1-Y))
        return dX
    return Y, logistic_bwd


def _zero_init(model):
    def _zero_init_impl(self, X, y):
        self.W.fill(0)
    model.on_data_hooks.append(_zero_init_impl)
    return model

@layerize
def _preprocess_doc(docs, drop=0.):
    keys = [doc.to_array([LOWER]) for doc in docs]
    keys = [a[:, 0] for a in keys]
    ops = Model.ops
    lengths = ops.asarray([arr.shape[0] for arr in keys])
    keys = ops.xp.concatenate(keys)
    vals = ops.allocate(keys.shape[0]) + 1
    return (keys, vals, lengths), None


def build_text_classifier(nr_class, width=64, **cfg):
    with Model.define_operators({'>>': chain, '+': add, '|': concatenate, '**': clone}):
        embed_lower = HashEmbed(width, 300, column=1)
        embed_prefix = HashEmbed(width//2, 300, column=2)
        embed_suffix = HashEmbed(width//2, 300, column=3)
        embed_shape = HashEmbed(width//2, 300, column=4)

        cnn_model = (
            FeatureExtracter([ORTH, LOWER, PREFIX, SUFFIX, SHAPE])
            >> _flatten_add_lengths
            >> with_getitem(0,
                (embed_lower | embed_prefix | embed_suffix | embed_shape) 
                >> Maxout(width, width+(width//2)*3)
                >> Residual(ExtractWindow(nW=1) >> ReLu(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> ReLu(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> ReLu(width, width*3))
            )
            >> Pooling(mean_pool, max_pool)
            >> Residual(ReLu(width*2, width*2))
            >> _zero_init(Affine(nr_class, width*2, drop_factor=0.0))
        )

        linear_model = (
            _preprocess_doc
            >> LinearModel(width*2)
            >> ReLu(nr_class, width*2)
        )

        #model = (linear_model + cnn_model) >> logistic
        model = cnn_model >> _logistic
        #model = linear_model >> logistic
    model.lsuv = False
    return model

