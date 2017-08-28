import pandas as pd
import s3client


__author__ = 'Junya Kaneko <jyuneko@hotmail.com>'


def read_csv(s3path_or_s3file, *args, **kwargs):
    if isinstance(s3path_or_s3file, str):
        s3csv = s3client.file.S3File(s3path_or_s3file)
    elif isinstance(s3path_or_s3file, s3client.file.S3File):
        s3csv = s3path_or_s3file
    else:
        raise ValueError
    is_generator = False
    with s3csv.open('r') as f:
        df = pd.read_csv(f, *args, **kwargs)
        if isinstance(df, pd.io.parsers.TextFileReader):
            is_generator = True
            for row in df:
                yield row
    if not is_generator:
        return DataFrame.create_from_pddf(df)


class DataFrame:
    def __init__(self, *args, **kwargs):
        self._pddf = pd.DataFrame(*args, **kwargs)

    @staticmethod
    def create_from_pddf(pddf):
        df = DataFrame()
        df._pddf = pddf
        return df

    def from_csv(self):
        raise NotImplementedError

    def to_csv(self, s3path_or_s3file, *args, **kwargs):
        if isinstance(s3path_or_s3file, str):
            s3csv = s3client.file.S3File(s3path_or_s3file)
        elif isinstance(s3path_or_s3file, s3client.file.S3File):
            s3csv = s3path_or_s3file
        else:
            raise ValueError
        with s3csv.open('w') as f:
            self._pddf.to_csv(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._pddf, name)
