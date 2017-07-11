"""
Implementation of thresholded SVD based topic modelling algorithm.
Python wrapper for original matlab implementation by Trapit Bansal

The class TSVD takes the datasetname, corpus input, vocabulary and number of topics as minimal
arguments to run the model. In evaluation mode, several inferences and patters can be discovered
that may be used to discover diagnostic information regarding the performance.
"""

from __future__ import print_function
from __future__ import division

from topiceval.basemodel import BaseModel
import topiceval.thresholdedsvd.hyperparams as hyperparams
import topiceval.utils as utils

import numpy as np
import scipy.sparse
import scipy.sparse.linalg
from scipy.optimize import minimize
from sklearn.cluster import KMeans, MiniBatchKMeans

import logging
from math import floor, ceil, sqrt
import os
import pickle


class TSVD(BaseModel):
    def __init__(self, datasetname="_", learn_model=True, A_matrix_path=None, id2word_dict=None, id2word_dict_path=None,
                 corpus=None, corpus_path=None, vocab_filepath=None, docword_filepath=None, vocab_size=None,
                 num_docs=None, num_topics=None, M_matrix_path=None, W_matrix_path=None, evaluation_mode=True):
        """
        Make TSVD model

        Given corpus, vocabulary and number of topics, learn a model OR
        Given the M matrix, carry on with evaluation mode

        One of A_matrix_path, corpus, corpus_path must be given when learning model

        One of id2word_dict, id2word_dict_path, vocab_filepath must be given

        When not learning, M_matrix_path should be given, if evaluation_mode is set
        then W_matrix_path as well

        vocab_size and num_docs are optional and used to confirm user's values with the
        dimensions of constructed matrices

        num_topics must be provided when learning model


        Parameters
        ----------
        :param datasetname: string, name of dataset on which model is learnt, "_" by default

        :param learn_model: bool, Whether to learn the model or use precomputed learned
            matrices

        :param A_matrix_path: string, filepath where doc-term matrix for the corpus is stored

        :param id2word_dict: dictionary object, word_id to word dictionary

        :param id2word_dict_path: string, filepath to id2word_dict

        :param corpus: mm list, denoting term word frequency distribution of corpus

        :param corpus_path: string, filepath to .npy corpus file

        :param vocab_filepath: string, filepath to text file with vocabulary words

        :param docword_filepath: string, filepath to docword text file, in format
            doc_id word_id word_frequency where id's are 0-indexed

        :param vocab_size: int, vocabulary size

        :param num_docs: int, number of docs in corpus

        :param num_topics: int, number of topics to learn

        :param M_matrix_path: string, path to pre-computed M matrix

        :param W_matrix_path: string, path to pre-computed W matrix

        :param evaluation_mode: bool, whether to learn W matrix for diagnostics

        """
        self.modelname = "tsvd"
        super(TSVD, self).__init__(datasetname=datasetname, id2word_dict=id2word_dict, A_matrix_path=A_matrix_path,
                                   id2word_dict_path=id2word_dict_path, corpus=corpus,
                                   corpus_path=corpus_path, vocab_filepath=vocab_filepath,
                                   docword_filepath=docword_filepath, vocab_size=vocab_size, num_docs=num_docs,
                                   evaluation_mode=True, Amatrix_needed=(A_matrix_path is None) or evaluation_mode)

        self.num_topics = num_topics
        self.topicwise_catchwords = []
        self.results_directory = "./data/tsvd/results_%s_eps1_%0.2f_eps2_%0.2f_eps3_%0.2f_topics_%d/" \
                                 % (self.datasetname, hyperparams.eps1_c, hyperparams.eps2_c, hyperparams.eps3_c,
                                    self.num_topics)
        # if not os.path.exists(self.results_directory):
        #     os.makedirs(self.results_directory)

        if A_matrix_path is not None:
            utils.verify_filename(A_matrix_path)
            if A_matrix_path[-4:] == ".npy":
                self.A_matrix = np.load(A_matrix_path)
            elif A_matrix_path[-4:] == ".npz":
                self.A_matrix = scipy.sparse.load_npz(A_matrix_path)
            else:
                logging.warning("Unrecognized format, loading through pickle...")
                with open(A_matrix_path, "rb") as handle:
                    self.A_matrix = pickle.load(handle).T

        if not scipy.sparse.isspmatrix_csc(self.A_matrix):
            self.A_matrix = scipy.sparse.csc_matrix(self.A_matrix)

        self.A_matrix_norm = self.__get_normalized_A_matrix()

        if not learn_model and (M_matrix_path is None or W_matrix_path is None):
            raise ValueError("Learn model option is off and M and W matrix paths havent been provided.")

        if learn_model:
            if self.num_topics is None:
                raise ValueError("Num_topics not provided (learn_model option is on)")
            if M_matrix_path is not None or W_matrix_path is not None:
                logging.warning("User given filepath for M/W discarded in favor of learn_model=True")

            # Deciding number of repitions in k-means clustering while learning M matrix
            if self.num_docs <= 5000:
                reps = 5
            elif self.num_docs >= 50000:
                reps = 1
            else:
                reps = 3

            self.M_matrix = self.__learn_M_matrix(reps=reps, write_thresholds=False, write_catchwords=False)

            if evaluation_mode:
                self.W_matrix = self.learn_W_matrix()
            else:
                self.W_matrix = None
        else:
            if M_matrix_path is None or (evaluation_mode is True and W_matrix_path is None):
                raise ValueError("If learn_model option is off, both M and W matrix paths need to be given in "
                                 "evaluation mode")
            utils.verify_filename(M_matrix_path)
            self.M_matrix = np.load(M_matrix_path)

            if evaluation_mode:
                self.W_matrix = np.load(W_matrix_path)
                utils.verify_filename(W_matrix_path)
                if self.num_topics is not None:
                    assert (self.W_matrix.shape[0] == self.num_topics)
                else:
                    assert (self.M_matrix.shape[1] == self.W_matrix.shape[0])

            if self.num_topics is not None:
                assert (self.M_matrix.shape[1] == self.num_topics)
            self.num_topics = self.M_matrix.shape[1]

        # Get topic-weight tuples for learned topics, 30 word-weight pairs per topic
        self.representative_topic_tuples = self.get_representative_topic_tuples(num_topics=None, wordspertopic=30)
        return

    def __learn_M_matrix(self, reps, write_thresholds=False, write_catchwords=False, save_B_Thresholds=False):
        logging.info("Starting learning M matrix...")
        d = self.num_docs
        w = self.vocab_size
        K = self.num_topics
        logging.debug("d=%d, w=%d, K=%d" % (d, w, K))

        B, word_thresholds = self.__sparse_threshold(hyperparams.w0_c / self.num_topics, hyperparams.eps1_c, d, w)

        if save_B_Thresholds:
            logging.info("Saving B matrix and word thresholds...")
            try:
                scipy.sparse.save_npz(self.results_directory + "Bmatrix.npz", B)
                np.save(self.results_directory + "word_thresholds.npy", word_thresholds)
                logging.info("Done saving B matrix and word thresholds")
            except AttributeError:
                logging.error("Could not save B matrix (didn't save thresholds). Please update scipy version to 0.19.0")

        if write_thresholds:
            logging.info("Writing thresholds to file...")
            with open(self.results_directory + "word_thresholds.txt", "w") as f:
                for i, threshold in enumerate(word_thresholds):
                    f.write(self.id2word_dict[i] + " : %0.2f\n" % threshold)
            logging.info("Completed writing thresholds to file")

        retained_docs = np.array([idx for idx in range(d) if len(B[:, idx].indices) != 0])
        logging.info("Number of retained docs = %d out of %d" % (len(retained_docs), d))
        B = B[:, retained_docs]

        logging.info("Computing SVD projection of sparse matrix B")
        if w * d <= 5e7 and w > d:
            logging.info("SVD on B to get B(k)")
            _, S, V = scipy.sparse.linalg.svds(B, k=self.num_topics, return_singular_vectors="vh")
            assert (S.shape[0] == V.shape[0]), "S and V from SVD not matching in shape for subsequent multiplication"
            intermed_Bk = np.multiply(V, S.reshape(-1, 1))
            assert (intermed_Bk.shape[0] == K and intermed_Bk.shape[1] == d)
            BkT = scipy.sparse.csr_matrix(intermed_Bk.T)
        else:
            logging.info("Computing SVD via top-k eigenvector route")
            BBt = B.dot(B.transpose())
            _, U = scipy.sparse.linalg.eigsh(BBt, k=self.num_topics, which='LM')
            # noinspection PyRedundantParentheses
            BkT = scipy.sparse.csr_matrix(B.transpose().dot(U))
        logging.info("Computation of BkT complete")
        logging.debug("Shape of BkT = {}".format(BkT.shape))

        logging.info("Starting K-Means on BkT")
        if d >= 8000:
            kmeansB_k = MiniBatchKMeans(n_clusters=K, init="k-means++", n_init=reps*2, verbose=0,
                                        random_state=1).fit(BkT)
        else:
            kmeansB_k = KMeans(n_clusters=K, init="k-means++", n_init=reps, verbose=0, random_state=1).fit(BkT)
        logging.debug("Clusetering intertia on B_k = %0.3f" % kmeansB_k.inertia_)
        cluster_id = kmeansB_k.labels_

        # Finding cluster centers in original space
        centers = np.zeros((K, w))
        logging.debug("B_k CLUSTERING INFO:")
        for k_iter in range(K):
            cluster_docs = np.where(cluster_id == k_iter)[0]
            logging.debug("Label:%2d Num_Docs:%4d" % (k_iter, len(cluster_docs)))
            logging.debug("Documents: {}".format(cluster_docs))
            logging.debug("Num Docs: %d", )
            centers[k_iter, :] = (B[:, cluster_docs].sum(axis=1).reshape(-1))/len(cluster_docs)
        logging.info("Starting clustering on B matrix")
        kmeansB = KMeans(n_clusters=K, init=centers, verbose=0, random_state=1, n_init=1).fit(B.transpose())
        cluster_id = kmeansB.labels_
        logging.info("Completed clustering on B matrix")

        logging.info("Starting topic matrix computation without catchwords")
        M_matrix_nlcatchwords = np.zeros((w, K))
        for k_iter in range(K):
            cols = retained_docs[np.where(cluster_id == k_iter)[0]]
            M_matrix_nlcatchwords[:, k_iter] = self.A_matrix_norm[:, cols].sum(axis=1).A[:, 0]/len(cols)
        logging.info("Completed topic matrix computation without catchwords")

        logging.info("Starting to find catchwords...")
        fractiles = np.zeros((w, K))                # fractiles will store g(i, l) values
        cw_threshold = int(floor(hyperparams.eps2_c*hyperparams.w0_c*d/(2*K)))
        # TODO: Make T sparse as well
        for l in range(K):
            T = self.A_matrix_norm[:, retained_docs[np.where(cluster_id == l)[0]]].transpose().toarray()
            T.sort(axis=0)
            T = T[::-1, :]                          # Sorted columns in descending order
            if cw_threshold > T.shape[0]:
                logging.warning("Warning: Cluster num %d has lesser documents (%d) than threshold (%d)"
                                % (l, T.shape[0], cw_threshold))
                idx = T.shape[0]
            else:
                idx = cw_threshold
            fractiles[:, l] = T[idx - 1, :]
            logging.debug("fractile[{0}] = {1}".format(l, fractiles[:, l]))
        catchword_mm = [[]]*K
        rho = hyperparams.rho_c
        for l in range(K):
            for i in range(w):
                cfractile = fractiles[i, l]
                isanchor = False
                for l2 in range(K):
                    if l2 == l:
                        continue
                    otherfractile = fractiles[i, l2]
                    isanchor = cfractile > rho*otherfractile
                    if not isanchor:
                        break
                if isanchor:
                    catchword_mm[l] = catchword_mm[l] + [i]
        for topic_cws in catchword_mm:
            self.topicwise_catchwords += [[self.id2word_dict[word_idx] for word_idx in topic_cws]]
        logging.info("Completed finding catchwords")
        sum_catchwords = np.array([len(topic_cw) for topic_cw in catchword_mm])
        logging.debug("sum_catchwords = {}".format(sum_catchwords))
        catchy_topics = np.where(sum_catchwords != 0)[0]
        catchy_topics_set = set(catchy_topics)
        catchless_topics = set(range(K)) - catchy_topics_set
        logging.info("Initial number of topics without catchwords: %d(of %d)" % (len(catchless_topics), K))
        word_sums = self.A_matrix_norm.sum(axis=1).A[:, 0]
        lower_collective_threshold = 0.01*d/(2*K)
        for l in range(K):
            if l in catchy_topics_set and sum(word_sums[catchword_mm[l]]) <= lower_collective_threshold:
                catchless_topics.add(l)
                catchy_topics_set.remove(l)
                logging.info("Topic %d added to catchless topics due to lower collective threshold" % l)

        if write_catchwords:
            logging.info("Writing catchwords to file...")
            with open("./data/tsvd_topic_catchwords_" + self.datasetname + ".txt", "w") as f:
                for l in range(K):
                    f.write("------Topic #%d: num_cw = %3d------\n" % (l, len(catchword_mm[l])))
                    for word_idx in catchword_mm[l]:
                        f.write(self.id2word_dict[word_idx] + ", ")
                    f.write("\n\n")
            logging.info("Completed writing catchwords to file\n")

        logging.info("Final Catchless Topics: %d(of %d)" % (len(catchless_topics), K))
        logging.info("Catchless topics: {}".format(catchless_topics))

        documents_threshold = int(max(floor(hyperparams.eps3_c * hyperparams.w0_c * d / (2 * K)), 1))
        logging.debug("Document number threshold for computing M matrix: %0.3f" % documents_threshold)

        logging.info("Computing M matrix...")
        M_matrix = np.zeros((w, K))
        # TODO: This is just a quick fix, will require extra memory to store another csr matrix
        Arow = scipy.sparse.csr_matrix(self.A_matrix_norm)
        for l in range(K):
            if l in catchless_topics:
                M_matrix[:, l] = M_matrix_nlcatchwords[:, l]
                continue
            doc_sums = Arow[catchword_mm[l], :].sum(axis=0).A[0, :]
            document_indices_sorted = np.argsort(doc_sums)[::-1]
            doc_sums_sorted = doc_sums[document_indices_sorted]
            if doc_sums[document_indices_sorted[documents_threshold]] == 0:
                logging.warning("Topic %d, doc sum is 0 at document threshold" % l)
                # We will only take documents that have >0 sum in this case
                least_nnz_idx = 0
                # TODO: This is inefficient, replace with binary search to get >0 element
                while least_nnz_idx < len(doc_sums_sorted) and doc_sums_sorted[least_nnz_idx] > 0:
                    least_nnz_idx += 1
                top_document_indices = document_indices_sorted[0:least_nnz_idx]
            else:
                keep_till_index = documents_threshold
                threshold_doc_sum = doc_sums_sorted[keep_till_index]
                while keep_till_index + 1 < len(doc_sums_sorted) \
                        and doc_sums_sorted[keep_till_index + 1] == threshold_doc_sum:
                    keep_till_index += 1
                top_document_indices = document_indices_sorted[0:keep_till_index]

            M_matrix[:, l] = self.A_matrix_norm[:, top_document_indices].sum(axis=1).A[:, 0] / len(
                top_document_indices)
        logging.info("Completed learning M matrix\n")

        # Uncomment to get normalized (each column sum = 1) M matrix
        # logging.info("Normalizing M matrix...")
        # M_matrix = self.__normalize_M_matrix(M_matrix)
        return M_matrix

    @staticmethod
    def __normalize_M_matrix(M):
        for col in range(M.shape[1]):
            M[:, col] = M[:, col]/sum(M[:, col])
        return M

    def __sparse_threshold(self, omega1, omega2, d, w):
        logging.info("Starting sparse thresholding on matrix A")
        threshold1 = int(min(floor(omega1*d/2), d))
        threshold2 = 3*omega2*omega1*d
        logging.debug("threshold1: %0.3f     threshold2: %0.3f" % (threshold1, threshold2))
        estimated_nnz = int(floor(self.A_matrix.count_nonzero()/10))
        logging.debug("estimated nnz = %d" % estimated_nnz)
        id_cols = np.zeros(estimated_nnz)
        id_rows = np.zeros(estimated_nnz)
        values = np.zeros(estimated_nnz)
        allocated_space = estimated_nnz
        nnz_B = 0
        word_thresholds = np.zeros(w)
        # TODO: Memory considerations here?
        A = scipy.sparse.csr_matrix(self.A_matrix_norm)
        for i in range(w):
            logging.debug("itr_num: %d" % i)
            word_distribution_unsorted = A[i, :]
            data, indices = [], []

            for idx in range(len(word_distribution_unsorted.data)):
                val = round(word_distribution_unsorted.data[idx]*self.avg_doc_size)
                if val > 0:
                    data.append(val)
                    indices.append(word_distribution_unsorted.indices[idx])

            word_distribution_unsorted = scipy.sparse.csr_matrix((data, indices, [0, len(indices)]), shape=(1, d))
            data = np.sort(word_distribution_unsorted.data)[::-1]
            indices = np.arange(len(word_distribution_unsorted.data))
            indptr = word_distribution_unsorted.indptr
            word_distribution = scipy.sparse.csr_matrix((data, indices, indptr), shape=(1, d))
            zeta = word_distribution[0, threshold1]

            def eq_zeta(_zeta, distribution):
                num_eq, next_val = 0, 0
                for dataval in distribution.data:
                    if dataval > _zeta:
                        continue
                    elif dataval == _zeta:
                        num_eq += 1
                    else:
                        next_val = dataval
                        break
                return num_eq, next_val

            while zeta != 0.:
                num_eq_zeta, next_val_zeta = eq_zeta(zeta, word_distribution)
                if num_eq_zeta < threshold2:
                    break
                else:
                    zeta = next_val_zeta
            word_thresholds[i] = zeta
            if zeta <= 1:
                logging.debug("Warning: Threshold for word %d is <= 1" % i)
                try:
                    elem = word_distribution.data[-1]
                    word_thresholds[i] = elem
                    logging.debug("Low threshold word %d threshold changed from %0.2f to %0.2f"
                                  % (i, zeta, word_thresholds[i]))
                except IndexError:
                    logging.debug("Warning: Low threshold word %d has no non-zero entry, threshold is < 1" % i)
            logging.debug("word_distribution[%d] has zeta = %0.3f"
                          % (i, word_thresholds[i]))

            rdocs = [word_distribution_unsorted.indices[idx] for idx, dataval in
                     enumerate(word_distribution_unsorted.data) if dataval >= word_thresholds[i]]
            ndocs = len(rdocs)
            logging.debug("word_distribution[%d] has %d rdocs" % (i, ndocs))
            id_cols[nnz_B:nnz_B+ndocs] = rdocs
            id_rows[nnz_B:nnz_B+ndocs] = [i]*ndocs
            values[nnz_B:nnz_B+ndocs] = [sqrt(word_thresholds[i])]*ndocs
            nnz_B += ndocs

            if float(nnz_B) >= allocated_space/2:
                logging.debug("Allocating more space, allocated space = %d, nnz_B = %d" % (allocated_space, nnz_B))
                id_cols = np.concatenate((id_cols, np.zeros(estimated_nnz)))
                id_rows = np.concatenate((id_rows, np.zeros(estimated_nnz)))
                values = np.concatenate((values, np.zeros(estimated_nnz)))
                allocated_space += estimated_nnz

        B = scipy.sparse.csc_matrix((values, (id_rows, id_cols)), shape=(self.vocab_size, self.num_docs))
        logging.debug("B MATRIX VALUES:")
        logging.debug("values = {0}\nid_rows = {1}\nid_cols = {2}".format(values, id_rows, id_cols))
        logging.info("Completed sparse thresholding on matrix A\n")
        return B, word_thresholds

    def learn_W_matrix(self):
        """
        TODO: This is extremely slow and unrequired, replace witth sparse coding function
        from bcd module (keeping sparsity = None)and pass l2 normalized A matrix (transposed)
        as X, transposed M matrix as H with parallelization=True

        Use constrined least square solver (scipy.minimize's slsqp), learn W matrix

        Parameters
        ----------
        :param self: TSVD object

        :return: learned W matrix of shape (num_topics, num_docs)
        """
        logging.info("Starting learning W matrix...")
        W = np.zeros((self.num_topics, self.num_docs))
        cons = tuple([{'type': 'eq', 'fun': lambda x: sum(x) - 1}])
        bounds = tuple([(0., 1.)]*self.num_topics)
        init_guess = np.full((self.num_topics, ), 1/self.num_topics)

        debug_progress_checkpoints = [round(elem * self.num_docs) for elem in np.arange(0.1, 1.1, 0.1)]
        for j in range(self.num_docs):
            logging.debug("iteration_num %d" % j)
            if j in debug_progress_checkpoints:
                logging.info("Completed inference progress: %d percent" % ceil(j * 100 / self.num_docs))
            Aj = self.A_matrix_norm[:, j].toarray()[:, 0]

            def loss_function(x):
                x = np.array(x).reshape(-1, 1)
                y = np.dot(self.M_matrix, x) - Aj.reshape(-1, 1)
                loss = np.linalg.norm(y, ord='fro')
                return loss

            res = minimize(loss_function, init_guess,
                           method='SLSQP', bounds=bounds, constraints=cons, options={'disp': False, 'maxiter': 50})
            w = res.x
            W[:, j] = w
            # logging.debug('SUM: %0.3f' % sum(w))
            # logging.debug('Min: %0.3f' % min(w))
            # dom_topic = np.argmax(w)
            # dom_topic_weight = w[dom_topic]
            # logging.debug('Max: %0.3f' % dom_topic_weight)
            # logging.debug('Dom Topic: %d' % dom_topic)
            # if not res.success:
            #     logging.warning("Failure on covergence for document id %d" % j)
            # final_error = loss_function(w)
            # logging.debug('Final Error = %0.3f' % final_error)
        logging.info("Completed learning W matrix\n")
        return W

    def __get_normalized_A_matrix(self):
        logging.info("Starting computation of normalized A matrix")
        doc_lengths = self.A_matrix.sum(axis=0)
        data = self.A_matrix.data
        indptr = self.A_matrix.indptr
        for j in range(self.A_matrix.shape[1]):
            dw = doc_lengths[0, j]
            if dw != 0:
                data[indptr[j]:indptr[j+1]] = data[indptr[j]:indptr[j+1]] / dw
        A_normalized = scipy.sparse.csc_matrix((data, self.A_matrix.indices, indptr), shape=self.A_matrix.shape)
        logging.info("Completed computation of normalized A matrix")
        return A_normalized

    def save_M_matrix(self, M_matrix_filename="M.npy"):
        """ Save TSVD object's learned M matrix at specified filepath as .npy file"""
        np.save(M_matrix_filename, self.M_matrix)
        return

    def save_W_matrix(self, W_matrix_filename="W.npy"):
        """ Save TSVD object's learned W matrix at specified filepath as .npy file"""
        np.save(W_matrix_filename, self.W_matrix)
        return

    def get_topic_tuples(self, topicid_list=None, wordspertopic=10):
        if topicid_list is None:
            logging.debug("Using all topics as topicid_list is none")
            topicid_list = range(self.num_topics)
        topic_tuples = []
        for topicid in topicid_list:
            topicid = int(topicid)
            topic_dist = self.M_matrix[:, topicid]
            topic_dist_norm = topic_dist/np.linalg.norm(topic_dist, ord=1)
            topic_topword_indices = np.argsort(self.M_matrix[:, topicid])[::-1][:int(wordspertopic)]
            topic_tuples.append([(self.id2word_dict[int(idx)].strip('\r'), topic_dist_norm[int(idx)])
                                 for idx in topic_topword_indices])
        return topic_tuples, topicid_list

    def plot_topic_topwords(self, topicid_list=None, wordspertopic=10, cmaps=None):
        topic_tuples, topicid_list = self.get_topic_tuples(topicid_list=topicid_list, wordspertopic=wordspertopic)
        super(TSVD, self).plot_topic_topwords_base(topic_tuples=topic_tuples, cmaps=cmaps, title='TSVD')
        return

    def plot_dominant_topic_document_distribution(self, upper_threshold=0.4, lower_threshold=0.3,
                                                  kind='vbar'):
        super(TSVD, self).plot_dominant_topic_document_distribution_base(W_matrix=self.W_matrix,
                                                                         upper_threshold=upper_threshold,
                                                                         lower_threshold=lower_threshold, kind=kind)
        return

    def plot_entropy_distribution(self, all_topics=True, topics=None, *args, **kwargs):
        if all_topics:
            if topics is not None:
                logging.warning("User given topic list discarded as all_topics=True")
            topics = range(self.num_topics)
        else:
            assert (topics is not None), "If all_topics option is switched off, list of topics to print must be given"
        distributions = [self.M_matrix[:, topic_id] for topic_id in topics]
        super(TSVD, self).plot_entropy_distribution_base(distributions, *args, **kwargs)
        return

    def plot_topic_entropy_colormap(self):
        distributions = [self.M_matrix[:, topic_id] for topic_id in range(self.num_topics)]
        super(TSVD, self).plot_topic_entropy_colormap(distributions)
        return

    def save_topic_top_words(self, filename, num_topics=None, wordspertopic=10, separator=","):
        if num_topics is None or num_topics > self.num_topics:
            topicid_list = range(self.num_topics)
            if num_topics is not None:
                logging.warning("Given num_topics > num_topics of model, selecting all topics")
        else:
            topicid_list = np.random.choice(self.num_topics, num_topics, replace=False)
        topic_tuples, _ = self.get_topic_tuples(topicid_list=topicid_list, wordspertopic=wordspertopic)
        super(TSVD, self).save_topic_top_words(word_weight_list=topic_tuples, filename=filename,
                                               separator=separator, datasetname=self.datasetname)
        return

    def get_representative_topic_tuples(self, num_topics=None, wordspertopic=30):
        if num_topics is None:
            num_topics = self.num_topics
        topicid_list = np.random.choice(self.num_topics, num_topics, replace=False)
        topic_tuples, _ = self.get_topic_tuples(topicid_list=topicid_list, wordspertopic=wordspertopic)
        return topic_tuples

    def save_topic_images(self, dirname):
        dirname = dirname + "tsvd/"
        if not os.path.exists(dirname):
            logging.debug("Creating directory %s" % dirname)
            os.makedirs(dirname)
        for i, topic_tuple in enumerate(self.representative_topic_tuples):
            super(TSVD, self).plot_topic_topwords_base(topic_tuples=[topic_tuple], cmaps='Uniform',
                                                       title='TSVD', save=True, show=False,
                                                       filename=dirname+"topic%d" % i, show_weight=True)
        return
