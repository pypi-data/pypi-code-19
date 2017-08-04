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
    def __init__(self, agg_by, date_field_name, unique_field_name, how_many=1):
        self.agg_by = agg_by
        self.date_field_name = date_field_name
        self.unique_field_name = unique_field_name
        self.how_many = how_many

    def fit(self, X, y=None):
        # stateless transformer
        return self

    def transform(self, X):

        sorted_df = X.sort_values([self.agg_by, self.date_field_name])
        groupped = sorted_df.groupby(self.agg_by, group_keys=False)
        for shift in range(1, 1 + self.how_many):
            col_name = "DELTA" + str(shift)

            X[col_name] = sorted_df[self.date_field_name] - sorted_df[self.date_field_name].shift(shift)

            for nth in range(shift):
                df2 = groupped.nth(nth)
                X.loc[X[self.unique_field_name].isin(df2[self.unique_field_name]), col_name] = None

        return X