"""
The :mod:`tslearn.shapelets` module gathers Shapelet-based algorithms.
"""

from sklearn.base import TransformerMixin
import numpy
from tslearn.utils import to_time_series_dataset

__author__ = 'Romain Tavenard romain.tavenard[at]univ-rennes2.fr'


def _shapelet_idx_match(Xi, shp):
    _check_monodim(Xi)
    Xi = Xi.reshape((-1, ))
    shp = shp.reshape((-1, ))
    sz = shp.shape[0]
    elem_size = Xi.strides[0]
    Xi_reshaped = numpy.lib.stride_tricks.as_strided(Xi, strides=(elem_size, elem_size),
                                                     shape=(Xi.shape[0] - sz + 1, sz))
    distances = numpy.linalg.norm(Xi_reshaped - shp, axis=1) ** 2
    return numpy.argmin(distances)

def _check_monodim(Xi):
    assert Xi.shape[1] == 1, "Shapelet models not implemented yet for multidimensional time series"


class ShapeletModel:
    def __init__(self, shapelet_lengths, d=1):
        self.n_shapelets = sum(shapelet_lengths.values())
        self.shapelet_lengths = shapelet_lengths
        self.d = d

        self.shapelets_ = []

    def fit(self, X, y=None):
        raise NotImplementedError

    def _idx_match(self, Xi, k):
        shp = self.shapelets_[k]
        return _shapelet_idx_match(Xi, shp)

    def _shapelet_transform(self, Xi):
        """
        Examples
        --------
        >>> from tslearn.utils import to_time_series
        >>> sh = ShapeletModel(shapelet_lengths={5: 1})
        >>> sh.shapelets_ = [numpy.array([1, 2, 3, 4, 5]).reshape((5, 1))]
        >>> ts = to_time_series(numpy.arange(100))
        >>> sh._shapelet_transform(ts)
        array([ 0.])
        """
        ret = numpy.empty((self.n_shapelets, ))
        for k in range(self.n_shapelets):
            shp = self.shapelets_[k]
            sz = shp.shape[0]
            ti = self._idx_match(Xi, k)
            ret[k] = numpy.linalg.norm(Xi[ti:ti+sz] - shp) ** 2 / sz
        return ret

    def _dM_dSkl(self, Xi, ti, Xj, tj, sz):
        return 2 * (Xj[tj:tj+sz] - Xi[ti:ti+sz]) / sz


class ConvolutionalShapeletModel(ShapeletModel):
    def __init__(self, shapelet_lengths, d=1):
        ShapeletModel.__init__(self, shapelet_lengths=shapelet_lengths, d=d)

    def fit(self, X, y=None):
        raise NotImplementedError

    def _idx_match(self, Xi, k):
        shp = self.shapelets_[k]
        _check_monodim(Xi)
        convs = numpy.correlate(Xi.reshape((-1, )), shp.reshape((-1, )), mode="valid")
        return numpy.argmax(convs)

    def _shapelet_transform(self, Xi):
        """
        Examples
        --------
        >>> from tslearn.utils import to_time_series
        >>> sh = ConvolutionalShapeletModel(shapelet_lengths={5: 1})
        >>> sh.shapelets_ = [numpy.array([1, 2, 3, 4, 5]).reshape((5, 1))]
        >>> ts = to_time_series(numpy.arange(100))
        >>> sh._shapelet_transform(ts)
        array([ 293.])
        """
        ret = numpy.empty((self.n_shapelets, ))
        for k in range(self.n_shapelets):
            shp = self.shapelets_[k]
            sz = shp.shape[0]
            ti = self._idx_match(Xi, k)
            ret[k] = numpy.sum(Xi[ti:ti+sz] * shp) / sz
        return ret

    def _dM_dSkl(self, Xi, ti, Xj, tj, sz):
        return - ShapeletModel._dM_dSkl(self, Xi, ti, Xj, tj, sz) / 2


class ShapeletTransform(TransformerMixin):
    def __init__(self, shapelets, squared_distances=False):
        self.squared_distances = squared_distances
        self.shapelets = to_time_series_dataset(shapelets, equal_size=False)

    @property
    def n_shapelets(self):
        return self.shapelets.shape[0]

    def fit_transform(self, X, y=None, **fit_params):
        X_ = to_time_series_dataset(X, equal_size=False)
        ret = numpy.empty((X_.shape[0], self.n_shapelets))
        for i in range(X_.shape[0]):
            for k in range(self.n_shapelets):
                shp = self.shapelets[k]
                sz = shp.shape[0]
                ti = _shapelet_idx_match(X_[i], shp)
                ret[i, k] = numpy.linalg.norm(X_[i][ti:ti+sz] - shp) ** 2 / sz
        if not self.squared_distances:
            ret = numpy.sqrt(ret)
        return ret
