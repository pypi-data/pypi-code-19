import math
import os
import re
import sys

import numpy
import pandas
from smart_open import smart_open

import lore


class Base(object):
    """
    Encoders reduces a data set to a more efficient representation suitable
    for learning. Encoders may be lossy, and should first be `fit` after
    initialization before `transform`ing data.
    """

    def fit(self, data):
        """
        Establishes the encoding for a data set

        :param data: representative samples
        """
        pass

    def transform(self, data):
        """
        :param data: to encode
        :return: encoded data
        """
        return data.apply(self.transform_datum)

    def reverse_transform(self, data):
        """
        Decodes data

        :param data: encoded set to be decoded
        :return: decoded data set
        """
        return data.apply(self.reverse_transform_datum)

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
        if data.dtype == numpy.object:
            return data
        
        return data.fillna(self.missing_value + addition)
    
    
    def cardinality(self):
        """
        The required array size for a 1-hot encoding of all possible values,
        including missing_value for encoders that distinguish missing data.
        
        :return: the unique number of values this encoding can transform
        """
        pass
    
    
class Norm(Base):
    """
    Encodes data between 0 and 1. Missing values are encoded to 0, and cannot be
    distinguished from the minimum value observed.
    """

    def __init__(self):
        self.__min = float('nan')
        self.__range = float('nan')
        self.missing_value = 0

    def fit(self, data):
        self.__min = float(data.min())
        self.__range = data.max() - self.__min + 1
        
    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return min(self.__range, max(0, datum - self.__min)) / self.__range

    def reverse_transform_datum(self, datum):
        return (datum * self.__range) + self.__min

    def cardinality(self):
        raise ValueError('Continuous values have infinite cardinality')


class LogNorm(Base):
    """
    Encodes log(value) between 0 and 1. Missing values are encoded to 0, and
    cannot be distinguished from the minimum value observed.
    """

    def __init__(self):
        self.__min = float('nan')
        self.__range = float('nan')
        self.missing_value = 0

    def fit(self, data):
        self.__min = math.log(data.min())
        self.__range = math.log(data.max()) - self.__min
        
    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return min(self.__range, max(0, math.log(datum) - self.__min)) / self.__range

    def reverse_transform_datum(self, datum):
        return (math.exp(datum) * self.__range) + self.__min

    def cardinality(self):
        raise ValueError('Continous values have infinite cardinality')


class Discrete(Base):
    """
    Discretizes continuous values into a fixed number of bins from [0,bins).
    Values outside of the fit range are capped between observed min and max.
    Missing values are encoded distinctly from all others, so cardinality is
    bins + 1.
    """
    
    def __init__(self, bins=10):
        self.__norm = bins - 1
        self.__min = float('nan')
        self.__range = float('nan')
        self.missing_value = self.__norm + 1
    
    def fit(self, data):
        self.__min = float(data.min())
        self.__range = data.max() - self.__min

    def transform_datum(self, datum):
        if datum is None or (isinstance(datum, float) and math.isnan(datum)):
            return self.missing_value
        else:
            return ((min(self.__range, max(0, datum - self.__min))) / self.__range) * self.__norm

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

    def fit(self, data):
        self.__max = data.max()
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


class ID(Base):
    """
    Encodes distinct values (regardless of type). Values that appear fewer than
    minimum_occurrences are mapped to a unique shared encoding to compress the
    long tail. New values that have not been previously observed will be
    distinctly encoded from the long tail values.
    """
    
    def __init__(self, minimum_occurrences=1):
        """
        :param minimum_occurrences: ignore ids with less than this many occurrences
        """
        self.minimum_occurrences = minimum_occurrences
        self.map = None
        self.inverse = None
        self.missing_value = 1
    
    def fit(self, data):
        ids = pandas.DataFrame({'id': data})
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
            return u'MISSING_VALUE'
        elif datum == 0:
            return u'LONG_TAIL'
        else:
            return self.inverse.get(datum)
    
    def cardinality(self):
        return len(self.map) + 2


class Token(ID):
    """
    Breaks sentences into individual words, and encodes each word individually,
    with the same properties as the ID encoder.
    """
    if sys.version_info.major == 2:
        PUNCTUATION_FILTER = re.compile(u'\W+\s\W+|\W+(\s|$)|(\s|^)\W+', re.UNICODE)
    elif sys.version_info.major == 3:
        PUNCTUATION_FILTER = re.compile('\W+\s\W+|\W+(\s|$)|(\s|^)\W+')

    def __init__(self, sequence_length=10, minimum_occurrences=1):
        """
        :param sequence_length: truncates tokens after sequence_length
        :param minimum_occurrences: ignore tokens with less than this many occurrences
        """
        super(Token, self).__init__(minimum_occurrences=minimum_occurrences)
        self.sequence_length = sequence_length
    
    def fit(self, data):
        super(Token, self).fit(
            pandas.Series(
                [token for sentence in data.apply(Token.tokenize)
                 for token in sentence]
            )
        )
    
    def transform_datum(self, datum):
        return [
            super(Token, self).transform_datum(token)
            for token in Token.tokenize(datum)
        ]
    
    def reverse_transform_datum(self, datum):
        return u' '.join([
            super(Token, self).reverse_transform_datum(token)
            for token in datum
        ])
    
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
            u' ',
            sentence
        ).lower().split()

        return []


class Glove(Token):
    """
    Encodes tokens using the GloVe embeddings.
    https://nlp.stanford.edu/projects/glove/
    https://blog.keras.io/using-pre-trained-word-embeddings-in-a-keras-model.html
    """

    def __init__(self, sequence_length=10, minimum_occurrences=1):
        """
        :param sequence_length: truncates tokens after sequence_length
        :param minimum_occurrences: ignore tokens with less than this many occurrences
        """
        super(Glove, self).__init__(minimum_occurrences=minimum_occurrences)
        self.sequence_length = sequence_length


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
        super(Token, self).fit(
            pandas.Series(
                [token for sentence in data.apply(Token.tokenize)
                 for token in sentence]
            )
        )

    def fit(self, data):
        self.missing_value = numpy.asarray([0.0] * self.dimensions, dtype='float32')
        self.map = {}
        self.inverse = {}

        path = os.path.join(lore.env.models_dir, 'encoders', 'glove.6B.%dd.txt.gz' % self.dimensions)
        local = app.data.download(path)
        with app.timer("Loading GloVe parameters: %s" % (local)):
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
