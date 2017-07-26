"""
© 2017. Case Recommender All Rights Reserved (License GPL3)

Item Most Similar Matrix Factorization - Item MSMF

"""

import numpy as np
from scipy.spatial.distance import squareform, pdist
from caserec.recommenders.rating_prediction.matrixfactorization import MatrixFactorization
from caserec.utils.extra_functions import timed
from caserec.utils.write_file import WriteFile

__author__ = "Arthur Fortes"


class MSMF(MatrixFactorization):
    def __init__(self, train_file, test_file, prediction_file=None, steps=30, learn_rate=0.01, delta=0.015, factors=10,
                 init_mean=0.1, init_stdev=0.1, baseline=False, similarity_metric='cosine', min_feedback=10):

        MatrixFactorization.__init__(self, train_file=train_file, test_file=test_file, steps=steps,
                                     learn_rate=learn_rate, delta=delta, factors=factors, init_mean=init_mean,
                                     init_stdev=init_stdev, baseline=baseline)
        self.prediction_file = prediction_file
        self.similarity_metric = similarity_metric
        self.min_feedback = min_feedback
        self.si_matrix = None

    def compute_similarity(self):
        # Calculate distance matrix between items
        self.si_matrix = np.float32(squareform(pdist(self.train_set['matrix'].T, self.similarity_metric)))
        # transform distances in similarities
        self.si_matrix = 1 - self.si_matrix

    def search_similar_item(self, item):
        item_index = self.train_set['mi'][item]
        similar_list = sorted(range(len(self.si_matrix[item_index])), key=lambda k: -self.si_matrix[item_index][k])
        for i in similar_list:
            if i != item_index and len(self.train_set['di'][self.train_set['map_item'][i]]) > self.min_feedback:
                return self.train_set['map_item'][i]

    def predict_test(self):
        cont_new_item = set()

        if self.test_set is not None:
            for user in self.test_set['users']:
                for item in self.test_set['feedback'][user]:
                    try:
                        # check if item is new in the dataset
                        if len(self.train_set['di'][item]) < self.min_feedback:
                            cont_new_item.add(item)
                            # if user is new, the algorithm find the user most similar with its and replace
                            item = self.search_similar_item(item)
                    except KeyError:
                        pass

                    u, i = self.map_users[user], self.map_items[item]
                    self.predictions.append((user, item, self._predict(u, i, True)))

            if self.prediction_file is not None:
                self.predictions = sorted(self.predictions, key=lambda x: x[0])
                WriteFile(self.prediction_file, self.predictions).write_recommendation()
            print("Cont num cold-start items:: " + str(len(cont_new_item)))
            return self.predictions

    def execute(self):
        # methods
        print("[Case Recommender: Rating Prediction > Item MSMF]\n")
        print("training data:: ", len(self.train_set['users']), " users and ", len(self.train_set['items']),
              " items and ", self.train_set['ni'], " interactions | sparsity ", self.train_set['sparsity'])
        print("test data:: ", len(self.test_set['users']), " users and ", len(self.test_set['items']),
              " items and ", (self.test_set['ni']), " interactions | sparsity ", self.test_set['sparsity'])

        # compute similarity
        self.compute_similarity()
        # train model
        print("training time:: ", timed(self.train_model), " sec")
        print("\nprediction_time:: ", timed(self.predict_test), " sec\n")
        self.evaluate(self.predictions)


dir_fold = "C:/Users/forte/OneDrive/msmf/datasets/filmtrust/folds/0/"
# MatrixFactorization(dir_fold + "train.dat", dir_fold + "test.dat").execute()
MSMF(dir_fold + "train.dat", dir_fold + "test.dat", min_feedback=10, similarity_metric='cosine').execute()
