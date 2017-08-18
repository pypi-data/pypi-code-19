"""Lsi Model."""
import os
import pickle

from sklearn.base import BaseEstimator, TransformerMixin


path = os.path.join(os.path.dirname(__file__), 'data/org_data.pkl')
with open(path, 'rb') as fp:
    data_names = pickle.load(fp)

path = os.path.join(os.path.dirname(__file__), 'data/name_list.pkl')
with open(path, 'rb') as fp:
    data_names = pickle.load(fp)


# keep this
class GensimLsi(BaseEstimator, TransformerMixin):
    """
    Custom sklearn transformer to convert tokenized,
    preprocessed data to tf-idf representation.
    """
    def __init__(self, id2word_path, lsi_path=None, index_path=None):
        self.num_topics = 10
        self.corpus = None
        self.index = None
        self.model = None
        self.id2word = self.load(id2word_path=id2word_path)
        if lsi_path is not None:
            self.model = self.load(lsi_path=lsi_path)
        if index_path is not None:
            self.index = self.load(index_path=index_path)

    @staticmethod
    def load(lsi_path=None, id2word_path=None, index_path=None):
        """
        If specified, attempts to load gensim LsiModel from `lsi_path`
        and gensim Dictionary from `dictionary_path`.

        Parameters
        ----------
        lsi_path: str
            File-path designating where self.model should be saved.
        id2word_path: str
            File-path designating where self.dictionary should be saved.
        """
        if lsi_path is not None:
            from gensim.models import LsiModel
            if not os.path.exists(lsi_path):
                raise IOError('The provided file path to the LsiModel was not found.'
                              'Please ensure that the argument is the correct path.')
            return LsiModel.load(lsi_path)
        if id2word_path is not None:
            from gensim.corpora.dictionary import Dictionary
            if not os.path.exists(id2word_path):
                raise IOError('The provided file path to the Dictionary was not found.'
                              'Please ensure that the argument is the correct path.')
            return Dictionary.load(id2word_path)
        if index_path is not None:
            from gensim.similarities import MatrixSimilarity
            if not os.path.exists(index_path):
                raise IOError('The provided file path to the Dictionary was not found.'
                              'Please ensure that the argument is the correct path.')
            return MatrixSimilarity.load(index_path)

    def save(self, lsi_path=None, id2word_path=None, index_path=None):
        """
        Saves objects from fit process: gensim.LsiModel to `lsi_path`
        and gensim.Dictionary to `dictionary_path`.
        If either self.model or self.dictionary does not exist, an
        AttributeError is raised.

        Parameters
        ----------
        lsi_path: str
            File-path designating where self.model should be saved.
        dictionary_path: str
            File-path designating where self.dictionary should be saved.
        """
        if not (self.model and self.id2word):
            raise AttributeError('Nothing to save yet, please run .fit first.')
        if lsi_path is not None:
            self.model.save(lsi_path)
        if id2word_path is not None:
            self.id2word.save(id2word_path)
        if index_path is not None:
            self.index.save(index_path)


    def fit(self, documents, num_topics=600, labels=None):
        """
        Fits a gensim LsiModel to documents.

        Parameters
        ----------
        documents: iterable
            List of documents. Each document must be a list of preprocessed tokens.
        labels: iterable
            Optional list of same size as documents, specifying label for each document.

        """
        from gensim.models import LsiModel
        from gensim.corpora.dictionary import Dictionary
        if self.id2word is None:
            raise AttributeError("Must specify id2word.")
        self.num_topics = num_topics
        self.model = LsiModel(documents, id2word=self.id2word, num_topics=600)
        self.corpus = self.model[documents]
        return self

    def transform(self, documents):
        """
        Returns a vectorized embedding of each document in documents.

        Parameters
        -----------
        documents: iterable
            List of documents. Each document must be a list of tokens.

        Returns
        -------
            iterable: list of vectorized documents.
        """
        if self.model is None:
            raise AttributeError('Must have a fit model in order'
                                 ' to call transform.')
        return self.model[documents]

    def similarity(self, doc, n=10):
        """
        Returns the `n` most similar items in `self.corpus`
        to `doc`.

        Parameters
        ----------
        doc:
            A document. embedded in same tfidf space as model.
        n: int (default=10)
            Number of most similar items to return.

        Returns
        -------
            sims: dictionary of (item, distance) key, value pairs sorted by
                similarity in descending order.
        """
        _n = n
        if self.model is None:
            raise AttributeError('Must have a fit model in order'
                                 ' to call similarity.')
        if self.index is None:
            print "no index, creating our own"
            print
            from gensim.similarities import MatrixSimilarity
            self.index = MatrixSimilarity(self.corpus)

        # if n is larger than the number of documents, return 1 result
        _n = n * (n < len(self.index)) + (1 - (n < len(self.index))) * 1

        if _n == 1:
            print("{n} too large a number, returning 1 result instead.").format(n=n)
        doc_lsi = self.model[doc]
        sims = self.index[doc_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])[0:_n]
        results = ["Org: {0} -- {s}".format(data_names[i].encode('utf8').strip(), s=j)
                   for i, j in sims]
        return results
