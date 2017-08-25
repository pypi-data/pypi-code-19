from __future__ import unicode_literals

import math
import os
import re
import sys
import logging
from datetime import timedelta

import inflection
import numpy
import pandas
from smart_open import smart_open

import lore
import lore.transformers
from lore.util import timer


logger = logging.getLogger(__name__)


class Base(object):
    """
    Encoders reduces a data set to a more efficient representation suitable
    for learning. Encoders may be lossy, and should first be `fit` after
    initialization before `transform`ing data.
    """

    def __init__(self, column, name=None):
        super(Base, self).__init__()
        
        self.column = column
        if name:
            self.name = name
        else:
            if isinstance(self.column, lore.transformers.Base):
                self.name = self.column.name
            else:
                self.name = self.column
            self.name = inflection.underscore(self.__class__.__name__) + '_' + self.name
        
    def fit(self, data):
        """
        Establishes the encoding for a data set

        :param data: representative samples
        """
        pass

    def transform(self, data):
        """
        :param data: DataFrame with column to encode
        :return: encoded Series
        """
        with timer(('transform %s:' % self.name), logging.DEBUG):
            return self.series(data).apply(self.transform_datum)

    def reverse_transform(self, series):
        """
        Decodes data

        :param data: encoded set to be decoded
        :return: decoded data set
        """
        return series.apply(self.reverse_transform_datum)

    def fit_transform(self, data):
        """
        Conveniently combine fit + transform on a data set

        :param data: representative samples
        :return: transformed data
        """
        self.fit(data)
        return self.transform(data)

    def fillna(self, data, addition=0):
        """
        Fills with encoder specific default values.

        :param data: examined to determine defaults
        :param addition: uniquely identify this set of fillnas if necessary
        :return: filled data
        """
        if self.series(data).dtype == numpy.object:
            return self.series(data)
        
        return self.series(data).fillna(self.missing_value + addition)
        
    def cardinality(self):
        """
        The required array size for a 1-hot encoding of all possible values,
        including missing_value for encoders that distinguish missing data.
        
        :return: the unique number of values this encoding can transform
        """
        pass

    def source_column(self):
        column = self.column
        while isinstance(column, lore.transformers.Base):
            column = column.column
        return column
    
    def series(self, data):
        if isinstance(self.column, lore.transformers.Base):
            series = self.column.transform(data)
        else:
            series = data[self.column]
        
        return series
        

class Match(Base):
    """ Provides elementwise comparison of left and right, see also numpy.equal
    """
    def __init__(self, column, other, name=None):
        if not name:
            column_name = column.name if isinstance(column, lore.transformers.Base) else column
            other_name = other.name if isinstance(other, lore.transformers.Base) else other
            name = 'match_' + column_name + '_and_' + other_name
        super(Match, self).__init__(column=column, name=name)
        self.other = other

    def fit(self, data):
        pass
    
    def transform(self, data):
        with timer(('transform %s:' % self.name), logging.DEBUG):
            return numpy.equal(self.series(data), self.other_series(data)).astype(float)
    
    def reverse_transform(self, data):
        return numpy.full((len(data),), 'LOSSY')

    def cardinality(self):
        return 2

    def other_series(self, data):
        if isinstance(self.other, lore.transformers.Base):
            return self.other.transform(data)
    
        return data[self.other]


class Continuous(Base):
    def __init__(self, column, name=None):
        super(Continuous, self).__init__(column, name)

    def cardinality(self):
        raise ValueError('Continous values have infinite cardinality')


class Pass(Base):
    def transform(self, data):
        return self.series(data)
    
    def reverse_transform(self, series):
        return series
    
    
class Norm(Continuous):
    """
    Encodes data between 0 and 1. Missing values are encoded to 0, and cannot be
    distinguished from the minimum value observed.
    """

    def __init__(self, column, name=None):
        super(Norm, self).__init__(column, name)
        self.__min = float('nan')
        self.__range = float('nan')
        self.missing_value = 0

    def fit(self, data):
        with timer(('fit %s:' % self.name), logging.DEBUG):
            series = self.series(data)
            self.__min = float(series.min())
            self.__range = series.max() - self.__min + 1

    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return min(self.__range, max(0, datum - self.__min)) / self.__range

    def reverse_transform_datum(self, datum):
        return (datum * self.__range) + self.__min

    
class LogNorm(Continuous):
    """
    Encodes log(value) between 0 and 1. Missing values are encoded to 0, and
    cannot be distinguished from the minimum value observed.
    """

    def __init__(self, column, name=None):
        super(LogNorm, self).__init__(column, name)
        self.__min = float('nan')
        self.__range = float('nan')
        self.missing_value = 0

    def fit(self, data):
        with timer(('fit %s:' % self.name), logging.DEBUG):
            series = self.series(data)
            self.__min = math.log(series.min())
            self.__range = math.log(series.max()) - self.__min
            logger.debug('  %s min: %s range: %s' % (self.name, self.__min, self.__range))

    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return min(self.__range, max(0, math.log(datum) - self.__min)) / self.__range

    def reverse_transform_datum(self, datum):
        return (math.exp(datum) * self.__range) + self.__min


class Boolean(Base):
    def transform(self, data):
        series = self.series(data)
        return series.astype(float)
    
    def reverse_transform(self, series):
        return series.round().astype(bool)


class Discrete(Base):
    """
    Discretizes continuous values into a fixed number of bins from [0,bins).
    Values outside of the fit range are capped between observed min and max.
    Missing values are encoded distinctly from all others, so cardinality is
    bins + 1.
    """
    
    def __init__(self, column, name=None, bins=10):
        super(Discrete, self).__init__(column, name)
        self.__norm = bins - 1
        self.__min = float('nan')
        self.__range = float('nan')
        self.missing_value = self.__norm + 1
        self.zero = 0.0
    
    def fit(self, data):
        with timer(('fit %s:' % self.name), logging.DEBUG):
            series = self.series(data)

            self.__min = series.min()
            self.__range = series.max() - self.__min
            if isinstance(self.__range, timedelta):
                self.zero = timedelta(0.0)
                
    def transform_datum(self, datum):
        if datum is None or \
                isinstance(datum, pandas._libs.tslib.NaTType) or \
                (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        elif self.__range == 0:
            return 0
        else:
            return (min(self.__range, max(self.zero, datum - self.__min)) * self.__norm) // self.__range
            
    def reverse_transform_datum(self, datum):
        if datum >= self.missing_value:
            return float('nan')
        else:
            return (datum / self.__norm * self.__range) + self.__min

    def cardinality(self):
        return self.__norm + 2


class Enum(Base):
    """
    Encodes a number of values from 0 to the max observed. New values that
    exceed previously fit max are capped. Missing values are distinctly encoded.
    """
    def __init__(self, column, name=None):
        super(Enum, self).__init__(column, name)

    def fit(self, data):
        with timer(('fit %s:' % self.name), logging.DEBUG):
            self.__max = self.series(data).max()
            self.missing_value = self.__max + 1

    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return min(self.__max, max(0, datum))
    
    def reverse_transform_datum(self, datum):
        if datum >= self.missing_value:
            return float('nan')
        else:
            return datum

    def cardinality(self):
        return self.__max + 1


class Unique(Base):
    """Encodes distinct values. Values that appear fewer than
    minimum_occurrences are mapped to a unique shared encoding to compress the
    long tail. New values that were not seen during fit will be
    distinctly encoded from the long tail values.
    """
    
    def __init__(self, column, name=None, minimum_occurrences=1):
        """
        :param minimum_occurrences: ignore ids with less than this many occurrences
        """
        super(Unique, self).__init__(column, name)
        self.minimum_occurrences = minimum_occurrences
        self.map = None
        self.inverse = None
        self.missing_value = 1
    
    def fit(self, data):
        with timer(('fit unique %s:' % self.name), logging.DEBUG):
            ids = pandas.DataFrame({'id': self.series(data)})
            counts = pandas.DataFrame({'n': ids.groupby('id').size()})
            qualified = counts[counts.n >= self.minimum_occurrences].copy()
            qualified['encoded_id'] = numpy.arange(len(qualified)) + 1
            
            self.map = qualified.to_dict()['encoded_id']
            self.inverse = {v: k for k, v in self.map.items()}
            self.missing_value = len(self.map) + 1
    
    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return self.map.get(datum, 0)
    
    def reverse_transform_datum(self, datum):
        if datum >= self.missing_value:
            return 'MISSING_VALUE'
        elif datum == 0:
            return 'LONG_TAIL'
        else:
            return self.inverse.get(datum)
    
    def cardinality(self):
        return len(self.map) + 2


class Token(Unique):
    """
    Breaks sentences into individual words, and encodes each word individually,
    with the same properties as the ID encoder.
    """
    PUNCTUATION_FILTER = re.compile(r'\W+\s\W+|\W+(\s|$)|(\s|^)\W+', re.UNICODE)

    def __init__(self, column, name=None, sequence_length=10, minimum_occurrences=1):
        """
        :param sequence_length: truncates tokens after sequence_length
        :param minimum_occurrences: ignore tokens with less than this many occurrences
        """
        super(Token, self).__init__(column, name, minimum_occurrences)
        self.sequence_length = sequence_length
    
    def fit(self, data):
        with timer(('fit token %s:' % self.name), logging.DEBUG):
            tokens = pandas.Series(
                [token for sentence in self.series(data).apply(Token.tokenize)
                 for token in sentence], copy=False
            )
        super(Token, self).fit(pandas.DataFrame({self.column: tokens}, copy=False))
    
    def transform_datum(self, datum):
        return [
            super(Token, self).transform_datum(token)
            for token in Token.tokenize(datum)
        ]
    
    def reverse_transform_datum(self, datum):
        return ' '.join([
            super(Token, self).reverse_transform_datum(token)
            for token in datum
        ])

    def get_token(self, tokens, i):
        if isinstance(tokens, float) or i >= len(tokens):
            return self.missing_value
        return tokens[i]

    @staticmethod
    def tokenize(sentence):
        if not sentence:
            return []
        
        if sys.version_info.major == 2:
            if not isinstance(sentence, unicode):
                if isinstance(sentence, str):
                    sentence = sentence.decode('utf-8')
                else:
                    sentence = unicode(sentence)
        
        if sys.version_info.major == 3:
            if not isinstance(sentence, str):
                sentence = str(sentence)
            
        return re.sub(
            Token.PUNCTUATION_FILTER,
            ' ',
            sentence
        ).lower().split()


class Glove(Token):
    """
    Encodes tokens using the GloVe embeddings.
    https://nlp.stanford.edu/projects/glove/
    https://blog.keras.io/using-pre-trained-word-embeddings-in-a-keras-model.html
    """

    def __init__(self, column, name=None, sequence_length=10, minimum_occurrences=1):
        """
        :param sequence_length: truncates tokens after sequence_length
        :param minimum_occurrences: ignore tokens with less than this many occurrences
        """
        super(Glove, self).__init__(column, name, sequence_length, minimum_occurrences)


    def __getstate__(self):
        # only pickle the bare necessities, pickling the GloVe encodings is
        # prohibitively inefficient
        return {
            'sequence_length': self.sequence_length,
            'dimensions': self.dimensions,
        }

    def __setstate__(self, newstate):
        # re-load the GloVe encodings after unpickling
        self.__dict__.update(newstate)
        self.fit(None)

    def fit(self, data):
        self.missing_value = numpy.asarray([0.0] * self.dimensions, dtype='float32')
        self.map = {}
        self.inverse = {}

        path = os.path.join(lore.env.models_dir, 'encoders', 'glove.6B.%dd.txt.gz' % self.dimensions)
        local = lore.io.download(path)
        with timer("Loading GloVe parameters: %s" % (local), logging.DEBUG):
            for line in smart_open(local):
                values = line.split()
                word = values[0]
                parameters = numpy.asarray(values[1:], dtype='float32')
                self.map[word] = parameters
                self.inverse[tuple(parameters.tolist())] = word

    def reverse_transform_datum(self, datum):
        return ' '.join([
            super(Token, self).reverse_transform_datum(tuple(token))
            for token in datum
        ])


class MiddleOut:
    """Creates an encoding out of a picking sequence

    Tracks the first d (depth) positions and the last d
    positions, and encodes all positions in-between to
    a middle value. Sequences shorter than 2d + 1 will
    not have a middle value encoding if they are even
    in length, and will have one (to break the tie) if
    they are odd in length.

    Args:
        depth (int): how far into the front and back
            of the sequence to track uniquely, rest will
            be coded to a middle value

    e.g.
        MiddleOut(2).transform([1,2,3,4,5,6,7]) =>
        [1, 2, 3, 3, 3, 4, 5]

    """
    
    def __init__(self, depth):
        self.depth = depth
    
    def fit(self, data):
        with timer("fit middle out: ", logging.DEBUG):
            pass
    
    def transform(self, x):
        max_seq = len(x)
        depth = self.depth
        this_depth = min(depth, max_seq // 2)
        
        res = numpy.full(max_seq, depth, dtype=int)
        res[:this_depth] = numpy.arange(this_depth)
        res[max_seq - this_depth:max_seq] = depth * 2 - numpy.arange(
            this_depth)[::-1]
        
        return res
    
    def cardinality(self):
        return self.depth * 2 + 1


class BatchSize:
    """Creates an encoding for batch size of a picking sequence

    Args:
        max_size (int): max size
        step (int): step size for encoding
    """

    def __init__(self, max_size, step):
        self.max_size = max_size
        self.step = step

    def transform(self, x):
        l = len(x)
        batch_size = (min(l, self.max_size) - 1) // self.step
        return numpy.repeat(batch_size, l)

    def cardinality(self):
        return self.max_size // self.step + 1


class Days:
    """Creates an encoding out of number of prior days

    Args:
        days_per_group (int): number of days to group together
    """

    def __init__(self, days_per_group):
        self.days_per_group = days_per_group
        self.max_days = None

    def fit(self, days):
        """Fit encoder to days array."""
        with timer("fit days: ", logging.DEBUG):
            self.max_days = numpy.max(days)

    def transform(self, days):
        """Transform days array."""
        days = numpy.minimum(days, self.max_days)
        days = numpy.maximum(days, 0)
        res = days // self.days_per_group
        return numpy.array(res)

    def cardinality(self):
        """Number of possible values the encoder may take"""
        return self.max_days // self.days_per_group + 1


class Single:
    """Create an encoding out of a single id.

    ids that appear fewer than min_size times are mapped to 1,
    as are new ids in the future. This retains the value 0
    to be used in padding, and identified in the future
    available set as an invalid availble position to be
    set to 0 in masking.

    Args:
        min_size (int): minimum support of id required.
    """
    def __init__(self, minimum_occurrences):
        self.minimum_occurrences = minimum_occurrences
        self.map = None

    def fit(self, ids):
        """Fit encoder to ids.

        Args:
            ids: an array of ids

        Return:
            a dict mapping ids to encoded ids
        """
        with timer("fit single:", logging.DEBUG):
            df = pandas.DataFrame({"ids": ids})
    
            counts = df.groupby("ids").size()
            counts = pandas.DataFrame({"n": counts})
    
            top = counts[counts.n >= self.minimum_occurrences].copy()
            top['encoded_id'] = numpy.arange(len(top)) + 2
            id_map = top.to_dict()['encoded_id']
    
            self.map = id_map

    def transform(self, ids):
        """Transforms ids into encoded IDs.

        New id values are encoded as 0s.

        Args:
            ids: an array of ids

        Return:
            array of encoded ids
        """
        res = [self.map.get(x, 1) for x in ids]

        return numpy.array(res)

    def cardinality(self):
        """Number of possible values the encoder may take

        Includes 0 and 1...max(compound_enc)
        """
        if len(self.map) == 0:
            return 1
        values = [val for val in self.map.values()]
        return numpy.array(values).max()
