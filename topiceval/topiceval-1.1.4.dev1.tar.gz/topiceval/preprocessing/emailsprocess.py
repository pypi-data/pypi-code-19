from __future__ import division
from __future__ import print_function

import topiceval.preprocessing.params as params

from gensim import corpora
from gensim.models import phrases
import numpy as np
import scipy.sparse
# import pandas as pd

from collections import defaultdict
import re
import logging


def remove_threads(text):
    """ Remove added messages from threaded mails, retaining only the most recent mail """
    text = re.sub(r'^From: .*', ' ', text, flags=re.MULTILINE | re.DOTALL)
    return text


def remove_signature(text):
    """ Remove signature elements, and following text entirely/until a new message is encountered"""
    signatures = ["regards", "best", "thanking you", "thanks", "sincerely", "warm regards", "best regards"]
    for signature in signatures:
        text = re.sub(r'^%s[^a-z]*?$.*?(<meta>){0, 1}' % signature, ' ', text,
                      flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    # for name in names:
    #     text = re.sub(r'^%s.*' % name, ' ', text, flags=re.IGNORECASE)
    return text


def phraser(text, bigram):
    """ Given gensim's phraser.Phraser instance, coalesce found bigrams in text """
    return ' '.join(bigram[text.split()])


def phrase_detection(df):
    """ Given the emails dataframe, form bigrams based on the text in "Body" field """
    sentences = [text.split() for text in df["Body"]]
    phrases_ = phrases.Phrases(sentences, min_count=params.bigrams_min_count, threshold=params.bigrams_threshold)
    bigram = phrases.Phraser(phrases_)
    # for phr, score in phrases_.export_phrases(sentences):
    #     print(u'{0}   {1}'.format(phr, score))
    return bigram


def remove_redundant_threads(df):
    bool_list = []
    df.sort_values(by=['ConversationID', 'SentOn'], ascending=[True, True])
    for i in range(0, df.shape[0]-1):
        if df.iloc[i]['ConversationID'] == df.iloc[i + 1]['ConversationID']:
            bool_list.append(False)
        else:
            bool_list.append(True)
    bool_list.append(True)
    return bool_list


def make_doc2bow(df, dirname):
    texts = [[word for word in document.split()] for document in df['CleanBody']]
    texts = prune_word_frequency(texts=texts, least_freq=params.word_least_corpus_frequency)
    id2word_dict = corpora.Dictionary(texts)
    ''' Prune n most frequent words '''
    id2word_dict.filter_n_most_frequent(params.filter_n_most_frequent)
    ''' Remove words in < word_least_document_frequency docs and in more than word_highest_document_fraction of docs, 
        and keep vocab size to maximum of max_vocab '''
    id2word_dict.filter_extremes(no_below=params.word_least_document_frequency,
                                 no_above=params.word_highest_document_fraction, keep_n=params.max_vocab)
    logging.info("vocabulary size: %d" % len(id2word_dict))
    ''' Making corpus '''
    corpus = [id2word_dict.doc2bow(text) for text in texts]
    ''' Truncate corpus by removing docs of length < document_min_length '''
    doc_indices_to_keep = truncate_corpus(corpus, min_len_doc=params.document_min_length)
    logging.info("Number of emails retained: %d (of %d)" % (len(doc_indices_to_keep), len(corpus)))
    trunc_corpus = [corpus[i] for i in doc_indices_to_keep]
    A = make_Amatrix_from_corpus(trunc_corpus, id2word_dict)
    ''' These are only aggregate statistics, no emails (or their metadata) can be reconstructed '''
    logging.info("Saving id2word_dict and corpus...")
    id2word_dict.save(dirname + 'id2word_dict.pickle')
    scipy.sparse.save_npz(dirname + "Amatrix.npz", A)
    np.save(dirname + "corpus.npy", trunc_corpus)
    np.save(dirname + "dfindices_in_corpus.npy", doc_indices_to_keep)
    return id2word_dict, trunc_corpus


def prune_word_frequency(texts, least_freq):
    """ Remove words based on corpus frequency.

    :param texts: list of lists, each list corresponds to a document, containing word tokens
    :param least_freq: words with corpus frequency below this are removed

    :return: texts (list of lists), with pruned word tokens
    """
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] >= least_freq] for text in texts]
    return texts


def len_doc(list_of_tups):
    length_doc = 0
    for tup in list_of_tups:
        length_doc += tup[1]
    return length_doc


def truncate_corpus(corpus, min_len_doc):
    good_indices = []
    for i, doc in enumerate(corpus):
        if len_doc(doc) >= min_len_doc:
            good_indices.append(i)
    return good_indices


def replace_names(text, names):
    for name in names:
        try:
            text = re.sub(r'%s' % name, '<name>', text)
        except:
            continue
    return text


def make_Amatrix_from_corpus(corpus, id2word_dict):
    # A = np.zeros((self.vocab_size, self.num_docs))
    vocab_size = len(id2word_dict)
    num_docs = len(corpus)
    A = scipy.sparse.dok_matrix((vocab_size, num_docs), dtype=np.float32)
    for doc_num in range(num_docs):
        for tup in corpus[doc_num]:
            A[tup[0], doc_num] = tup[1]
    return scipy.sparse.csr_matrix(A)
