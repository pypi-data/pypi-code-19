from sklearn.base import TransformerMixin


class StringLengthFilter(TransformerMixin):

    def __init__(self, field_name, length):
        self.field_name = field_name
        self.length = length

    def fit(self, X, y=None):
        # stateless transformer
        return self

    def transform(self, X):
        # assumes X is a DataFrame
        Xcols = X[X[self.field_name].str.len() > self.length]
        return Xcols