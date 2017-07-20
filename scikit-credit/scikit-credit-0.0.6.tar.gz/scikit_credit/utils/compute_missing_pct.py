__author__ = 'jiyue'


def compute_missing_pct(dataframe, dtype):
    dataframe.select_dtypes(include=[dtype]).describe().T \
        .assign(missing_pct=dataframe.apply(lambda x: (len(x) - x.count()) / float(len(x))))
