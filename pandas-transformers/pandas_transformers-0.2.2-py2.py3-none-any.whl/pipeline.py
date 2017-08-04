import pandas as pd

from sklearn.base import TransformerMixin


class DFFeatureUnion(TransformerMixin):
    # FeatureUnion but for pandas DataFrames

    def __init__(self, transformer_list, _on=None):
        self.transformer_list = transformer_list
        self._on = _on

    def fit(self, X, y=None):
        for (name, t) in self.transformer_list:
            t.fit(X, y)
        return self

    def transform(self, X):
        # assumes X is a DataFrame
        Xts = [t.transform(X) for _, t in self.transformer_list]
        Xunion = reduce(lambda X1, X2: pd.merge(X1, X2, on=self._on, left_index=not self._on, right_index=not self._on), Xts)

        return Xunion
