import pandas as pd
import numpy as np
import cPickle as pickle
import re
import os
from sklearn.cluster import MiniBatchKMeans


class Word2VecClusterTrainer(object):
    def __init__(self):
        self.completed_trainings = set()
        self.cluster_dicts = {}
        self.models = {}

    def completed_training(self, feature):
        training_id = self._get_w2v_training_id(feature)
        if training_id in self.completed_trainings:
            return True
        return False

    def train(self, feature, entityset, keep_loaded_data=False, time_last=None):
        feature.check_downloaded_corpus()
        corpus_path = feature.corpus_path
        # TODO: implement normalize
        obey_time_bounds = feature.obey_time_bounds_in_training
        unknown_misspelled_word = feature.unknown_misspelled_word

        _time_last = None
        if obey_time_bounds:
            _time_last = time_last
        all_words = self._get_all_words(feature.base_features[0],
                                        entityset,
                                        time_last=_time_last)

        words, vectors = self._convert_words_to_vectors(feature.base_features[0],
                                                        all_words, corpus_path,
                                                        unknown_misspelled_word,
                                                        keep_loaded_data=keep_loaded_data,
                                                        time_last=_time_last)

        if 3 * feature.cluster_batch_size > feature.num_clusters:
            init_size = 3 * feature.cluster_batch_size
        else:
            init_size = 3 * feature.num_clusters
        clusters = MiniBatchKMeans(n_clusters=feature.num_clusters,
                                   max_iter=feature.cluster_max_iter,
                                   max_no_improvement=feature.cluster_max_no_improvement,
                                   tol=feature.cluster_tol,
                                   batch_size=feature.cluster_batch_size,
                                   init_size=init_size,
                                   n_init=feature.cluster_n_init,
                                   reassignment_ratio=feature.cluster_reassignment_ratio,
                                   random_state=feature.random_state)
        clusters.fit(vectors)

        training_id = self._get_w2v_training_id(feature)
        self.cluster_dicts[training_id] = {}
        for word, label in zip(words, clusters.labels_):
            self.cluster_dicts[training_id][word] = label

        self.completed_trainings.add(training_id)

    def calculate_features(self, df, f):
        cluster_dict = self._get_cluster_dict(f)
        output_features = pd.Series([np.zeros(f.num_clusters, dtype=np.int32)
                                     for _ in xrange(len(df.index))],
                                    index=df.index)

        # TODO: do this with .apply()
        all_words = self._get_words_from_df(df)
        for row, words in all_words.iteritems():
            for word in words:
                if word in cluster_dict:
                    cluster = cluster_dict[word]
                    output_features.loc[row][cluster] += 1
        return output_features

    def _get_cluster_dict(self, feature):
        training_id = self._get_w2v_training_id(feature)
        assert training_id in self.completed_trainings,\
            "attempted to access cluster_dict of untrained feature"
        return self.cluster_dicts[training_id]

    def _word_splitter(self, text):
        words = re.findall(r"[\w']+", text)
        for word in words:
            yield word.lower()

    def _get_words_from_df(self, df):
        series = df[df.columns[0]]
        split = {}
        for index, text in series.iteritems():
            words = self._word_splitter(text)
            split[index] = words
        return split

    def _get_all_words(self, text_feature, entityset, time_last=None):
        """
        Right now this ignores instances
        """
        entity = text_feature.entity.id
        entityset = entityset.entity_stores[entity]
        col_name = text_feature.get_name()
        df = entityset.query_by_values(None,
                                   columns=[col_name],
                                   time_last=time_last)
        values = df[col_name].values
        for text in values:
            for word in self._word_splitter(text):
                yield word

    def _convert_words_to_vectors(self, feature, words, corpus_path,
                                  unknown_misspelled_word='skip',
                                  keep_loaded_data=False,
                                  time_last=None):
        from gensim.models import Word2Vec
        if unknown_misspelled_word != 'skip':
            msg = "Only available implementations for "
            msg += "unknown word imputation are 'skip', requested imputation: "
            msg += "{}".format(unknown_misspelled_word)
            raise NotImplementedError(msg)
        entityset = feature.entity.entityset.id
        entity = feature.entity.id
        data = self._load_vectors_from_pickle_file(entityset, entity, feature.get_name(),
                                                   corpus_path, time_last,
                                                   unknown_misspelled_word)
        if data is not None:
            new_words, vectors = data
            return new_words, vectors

        if corpus_path not in self.models:
            model = Word2Vec.load_word2vec_format(corpus_path, binary=True)
            if keep_loaded_data:
                self.models[corpus_path] = model
        else:
            model = self.models[corpus_path]

        new_words = []
        vectors = []
        for word in words:
            if word in model:
                vec = model[word]
                vectors.append(vec)
                new_words.append(word)
            elif unknown_misspelled_word == 'skip':
                print "WORD NOT IN MODEL:", word

        vectors = np.array(vectors)
        self._save_vectors_to_pickle_file(new_words, vectors,
                                          entityset, entity, feature.get_name(),
                                          corpus_path, time_last,
                                          unknown_misspelled_word)
        return new_words, vectors

    def _pck_fname(self, ds_id, eid, fname, corpus_path,
                   time_last, option):
        if time_last is None:
            time_last = ''
        else:
            time_last = time_last.strftime("%Y%m%s%H%M%S")
        fname = "corpus_data_{}.{}.{}_option_{}_{}.p".format(ds_id, eid, fname, time_last, option)
        pck_file = os.path.join(os.path.dirname(corpus_path), fname)
        return pck_file

    def _load_vectors_from_pickle_file(self, ds_id, eid, fname, corpus_path,
                                       time_last, option):
        pck_file = self._pck_fname(ds_id, eid, fname, corpus_path,
                                   time_last, option)
        if not os.path.exists(pck_file):
            return None
        with open(pck_file, 'rb') as fileobject:
            data = pickle.load(fileobject)
            if data is None:
                return None
            else:
                return data

    def _save_vectors_to_pickle_file(self, words, vectors,
                                     ds_id, eid, fname, corpus_path,
                                     time_last, option):
        pck_file = self._pck_fname(ds_id, eid, fname, corpus_path,
                                   time_last, option)
        with open(pck_file, 'wb') as fileobject:
            pickle.dump([words, vectors], fileobject)

    def _get_w2v_training_id(self, feature):
        # TODO: include cluster params?
        num_clusters = feature.num_clusters
        corpus = feature.corpus_name
        normalize = feature.normalize
        obey_time_bounds = feature.obey_time_bounds_in_training
        unknown_misspelled_word = feature.unknown_misspelled_word
        training_id = "w2v_{}_{}_{}_{}_{}".format(num_clusters,
                                                  corpus,
                                                  normalize,
                                                  obey_time_bounds,
                                                  unknown_misspelled_word)
        return training_id
