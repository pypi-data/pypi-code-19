from __future__ import print_function
from __future__ import division

import numpy as np
import scipy.sparse
from palmettopy.palmetto import Palmetto
from six.moves import xrange

from math import log


def umass_coherence(dirname, tuples, model, numwords=10, main_call=False):
    eps = 1e-12
    A = scipy.sparse.load_npz(dirname + "Amatrix.npz")
    is_sparse = True if scipy.sparse.isspmatrix(A) else False

    if not scipy.sparse.isspmatrix_csr(A):
        A = scipy.sparse.csr_matrix(A)

    pmis = []
    for topic_tuple in tuples:
        pmi_semantic = 0.
        for i in xrange(1, numwords):
            itup = topic_tuple[i]
            iwordid = model.word2id_dict[itup[0]]
            for j in xrange(0, i):
                jtup = topic_tuple[j]
                jwordid = model.word2id_dict[jtup[0]]

                if is_sparse:
                    w1_docs = set(A[iwordid, :].indices)
                    w2_docs = set(A[jwordid, :].indices)
                else:
                    w1_docs = set(np.where(A[iwordid, :] > 0)[0])
                    w2_docs = set(np.where(A[jwordid, :] > 0)[0])

                w1w2docs = w1_docs & w2_docs
                num = len(w1w2docs) + eps
                den = len(w2_docs)
                fraction = num/den
                pmi_semantic += log(fraction)
        if not main_call:
            model.representative_topics_umass_pmi.append(pmi_semantic)
        else:
            pmis.append(pmi_semantic)
    return pmis


def other_coherences(model, numwords=10):
    print("Calculating coherences via Palmetto tool...")
    palmetto = Palmetto()
    for topic_tuple in model.representative_topic_tuples:
        words = [tup[0] for tup in topic_tuple[:numwords]]
        uci_pmi, uci_npmi, cv_coherence = 0, 0, 0
        # uci_pmi = palmetto.get_coherence(words, coherence_type="uci")
        # uci_npmi = palmetto.get_coherence(words, coherence_type="npmi")
        # # umass_words = palmetto.get_coherence(words, coherence_type="umass")
        # cv_coherence = palmetto.get_coherence(words, coherence_type="cv")
        model.representative_topics_uci_pmi.append(uci_pmi)
        model.representative_topics_uci_npmi.append(uci_npmi)
        # model.representative_topics_umass_word_pmi.append(umass_words)
        model.representative_topics_cv_coherence.append(cv_coherence)
    print("Finished calculating other coherences!")
    return
