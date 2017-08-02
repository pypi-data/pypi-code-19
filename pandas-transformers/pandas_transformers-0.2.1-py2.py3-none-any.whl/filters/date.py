import pandas as pd

from sklearn.base import TransformerMixin

class DateFilter(TransformerMixin):

    def __init__(self, field_name, delta="30D"):
        self.field_name = field_name
        self.delta = pd.Timedelta(delta)


    def fit(self, X, y=None):
        # stateless transformer
        return self

    def transform(self, X):
        max_date = X[self.field_name].max() 
        # not in fit() method since we should not look 
        # exact date for test data we conceptually look
        # users last 14 days behaviour

        filtered_df = X[ max_date - self.delta < X[self.field_name]]
        return filtered_df
