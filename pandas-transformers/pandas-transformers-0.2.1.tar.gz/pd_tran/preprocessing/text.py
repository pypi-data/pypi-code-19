from sklearn.base import TransformerMixin

class SringReplacer(TransformerMixin):
   
    def __init__(self, _from, to):
        self._from = _from
        self.to = to


    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        cleaned = X.applymap(lambda x: str(x).replace(self._from, self.to))
        return cleaned
