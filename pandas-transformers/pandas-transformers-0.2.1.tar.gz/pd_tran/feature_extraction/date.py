import pandas as pd

from sklearn.base import TransformerMixin

class DateTimeFeatureExtractor(TransformerMixin):

    def __init__(self, agg_by, date_field_name, freq="1D", limit="30D", rel_field_name=None, round_to="1D"):
        self.limit = limit
        self.rel_field_name = rel_field_name
        self.date_field_name = date_field_name
        self.agg_by = agg_by
        self.freq = freq
        self.round_to = round_to

    def fit(self, X, y=None):
        # stateless transformer
        return self

    def transform(self, X):
        max_date = X[self.date_field_name].max().round(self.round_to)
        dates = pd.date_range(max_date - pd.Timedelta(self.limit), max_date, freq=self.freq)[1:]
        column_names = [self.agg_by]
        for i, date in enumerate(dates):
            column_name =  "%s_%s_%s" % (self.freq, self.rel_field_name or "COUNT", str(i))
            column_names.append(column_name)
            X[column_name] =  (
                            (date - pd.Timedelta(self.freq) < X[self.date_field_name]) & 
                                     (X[self.date_field_name] <= date )
                        ) * (X[self.rel_field_name] if self.rel_field_name else 1)

        new_df = X.groupby([self.agg_by]).sum()

        new_df.reset_index(inplace=True)

        return new_df[column_names] 


class DeltaTimeFeatureExtractor(TransformerMixin):
    def __init__(self, agg_by, date_field_name, how_many=1):
        self.agg_by = agg_by
        self.date_field_name = date_field_name
        self.how_many = how_many

    def fit(self, X, y=None):
        # stateless transformer
        return self

    def transform(self, X):

        def shift_method(frame):
            frame = frame.sort_values(self.date_field_name)
            for shift in range(self.how_many):
                frame['Delta' + str(shift+1)] = frame[self.date_field_name] - frame[self.date_field_name].shift(shift+1)
            return frame

        return X.groupby(self.agg_by, group_keys=False).apply(shift_method)






