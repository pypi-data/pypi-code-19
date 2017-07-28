import pandas as pd

from sklearn.base import TransformerMixin


class Converter(TransformerMixin):

    def __init__(self, _type):
        self._type = _type

    def fit(self, X, y=None):
        # stateless transformer
        return self

    def transform(self, X):
        # assumes X is a DataFrame
        Xcols = X.astype(self._type)
        return Xcols

class DateConverter(TransformerMixin):

    def __init__(self, field_name, format):
        self.format = format
        self.field_name = field_name

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        cleaned = X
        cleaned[self.field_name] = pd.to_datetime(X[self.field_name], format=self.format)
        return cleaned
