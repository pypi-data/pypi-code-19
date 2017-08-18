"""
Implementations algorithms for vectorizing text, all inheriting from sklearn BaseEstimators
and TransformerMixin.

This allows for use in pipeline objects, as well as provides a familiar API for preprocessing.

Example Code
-------------
>> from classypy.ml.transformers import TextProcessor
>> from classypy.ml.pipeline import process_and_vectorize_pipeline
>> tfidf = process_and_vectorize_pipeline(TextProcessor(), GensimTfid(use_sparse_representation=True))
>> tfidf.fit(data)
>> tfidf_data = list(tfidf.transform(data))  # call list because return is generator
"""

import os

from sklearn.base import BaseEstimator, TransformerMixin


class GensimBOW(BaseEstimator, TransformerMixin):
    """
    Custom sklearn transformer to convert tokenized,
    preprocessed data to bag-of-words representation.
    """

    def __init__(self, id2word_path=None, use_sparse_representation=False):
        """
        Parameters
        ----------
        id2word_path : str
            Path to location of gensim id2word dict.
            If specified, the model will load and use this object
            as its id2_word dict.
        use_sparse_representation: Boolean (default=False)
            When True, a sparse representation of the array is returned.
                Use this when feeding into a gensim model.
            When False, the full array is returned.
                Use this if feeding into sklearn estimator.
        """
        self.id2word = None
        self.use_sparse_representation = use_sparse_representation
        if id2word_path:
            self._load(id2word_path=id2word_path)

    def _load(self, id2word_path):
        """
        If self.id2word_path specified, loads gensim.id2word dict from path.

        Parameters
        ----------
        id2word_path: str
            File-path designating where self.id2word should be saved.
        """
        from gensim.corpora.dictionary import Dictionary
        if not os.path.exists(id2word_path):
            raise IOError('The provided file path to id2word_path was not found.'
                          'Please ensure that the argument is the correct path.')
        self.id2word = Dictionary().load(id2word_path)

    def save(self, id2word_path):
        """
        Saves self.id2word to id2word_path.
        If id2word does not exist, AttributeError is raised.

        Parameters
        ----------
        id2word_path: str
            File-path designating where self.id2word should be saved.
        """
        if not self.id2word:
            raise AttributeError('Nothing to save yet, please run .fit first.')
        self.id2word.save(id2word_path)

    def fit(self, documents, labels=None):
        """
        Creates map between words and their integer ids,
        storing it as `self.id2word`.

        Parameters
        ----------
        documents: iterable
            List of documents; each document a list of preprocessed tokens.
        labels:
            Optional list of same size as documents, specifying label for each document.
        """
        from gensim.corpora.dictionary import Dictionary
        self.id2word = Dictionary(documents)

    def transform(self, documents):
        """
        Converts a collection of words to its bag-of-words representation.

        Parameters
        ----------
        documents: iterable
            List of documents. Each document must be a list of tokens.

        Returns
        -------
            generator: yields vectorized representation of each document.
        """
        from gensim.matutils import sparse2full
        if self.id2word is None:
            raise AttributeError('Must have a fit id2word in order'
                                 ' to call transform.')

        def generator():
            """
            Closure to mutate return type depending on value of `use_sparse_representation`.
            """
            for document in documents:
                docbow = self.id2word.doc2bow(document)
                if self.use_sparse_representation:
                    yield docbow
                else:
                    yield sparse2full(docbow, len(self.id2word))
        return list(generator())


class GensimTfidf(BaseEstimator, TransformerMixin):
    """
    Custom sklearn transformer to convert tokenized,
    preprocessed data to tf-idf representation.
    """
    def __init__(self, tfidf_path=None, dictionary_path=None, use_sparse_representation=False):
        """
        Instantiate GensimTfidf object. If loading previously fit Dictionary and
        TfidfModel, you must specify a path to both the Dictionary and the TfidfModel.

        Parameters
        ----------
        tfidf_path : str
            Path to location of saved gensim TfidfModel.
            If specified, the model will load and use this object
            as its TfidfModel.
        dictionary_path : str
            Path to location of saved gensim Dictionary.
            If specified, the model will load and use this object
            as its Dictionary.
        use_sparse_representation: Boolean (default=False)
            When True, a sparse representation of the array is returned.
                Use this when feeding into a gensim model.
            When False, the full array is returned.
                Use this if feeding into sklearn estimator.
        """
        self.use_sparse_representation = use_sparse_representation
        self.dictionary = None
        self.tfidf = None
        # if both paths specified, load object
        if tfidf_path and dictionary_path:
            self._load(tfidf_path=tfidf_path, dictionary_path=dictionary_path)
        elif tfidf_path or dictionary_path:
            raise AttributeError('If loading pre-fit Dictionary and TfidfModel,'
                                 ' both must be specified, not just one.')

    def _load(self, tfidf_path, dictionary_path):
        """
        If specified, attempts to load gensim TfidfModel from `tfidf_path`
        and gensim Dictionary from `dictionary_path`.

        Parameters
        ----------
        tfidf_path: str
            File-path designating where self.tfidf should be saved.
        dictionary_path: str
            File-path designating where self.dictionary should be saved.
        """
        from gensim.models import TfidfModel
        from gensim.corpora.dictionary import Dictionary
        if not os.path.exists(tfidf_path):
            raise IOError('The provided file path to the TfidfModel was not found.'
                          'Please ensure that the argument is the correct path.')
        if not os.path.exists(dictionary_path):
            raise IOError('The provided file path to the Dictionary was not found.'
                          'Please ensure that the argument is the correct path.')
        self.tfidf = TfidfModel().load(tfidf_path)
        self.dictionary = Dictionary().load(dictionary_path)

    def save(self, tfidf_path, dictionary_path):
        """
        Saves objects from fit process: gensim.TfidfModel to `tfidf_path`
        and gensim.Dictionary to `dictionary_path`.
        If either self.tfidf or self.dictionary does not exist, an
        AttributeError is raised.

        Parameters
        ----------
        tfidf_path: str
            File-path designating where self.tfidf should be saved.
        dictionary_path: str
            File-path designating where self.dictionary should be saved.
        """
        if not (self.tfidf and self.dictionary):
            raise AttributeError('Nothing to save yet, please run .fit first.')
        self.tfidf.save(tfidf_path)
        self.dictionary.save(dictionary_path)

    def fit(self, documents, labels=None):
        """
        Fits a gensim TfidfModel to documents.

        Parameters
        ----------
        documents: iterable
            List of documents. Each document must be a list of preprocessed tokens.
        labels: iterable
            Optional list of same size as documents, specifying label for each document.

        """
        from gensim.models import TfidfModel
        from gensim.corpora.dictionary import Dictionary
        self.dictionary = Dictionary(documents)
        self.tfidf = TfidfModel(
            [
                self.dictionary.doc2bow(doc) for doc in documents
            ], id2word=self.dictionary)
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
        from gensim.matutils import sparse2full
        if self.dictionary is None:
            raise AttributeError('Must have a fit vocab in order'
                                 ' to call transform.')

        def generator():
            """
            Closure to mutate return type depending on value of `use_sparse_representation`.
            """
            for document in documents:
                vec = self.tfidf[self.dictionary.doc2bow(document)]
                if self.use_sparse_representation:
                    yield vec
                else:
                    yield sparse2full(vec, len(self.dictionary))
        return list(generator())

