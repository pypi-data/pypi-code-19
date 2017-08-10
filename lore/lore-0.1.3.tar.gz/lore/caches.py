import os
from os.path import exists, join
import pickle

from numpy import in1d
import pandas
from sklearn.model_selection import train_test_split

from lore import env
from lore.util import timer
import lore.io


class CSV(object):
    def __init__(self, key, dont_split=None):
        self.key = key
        self.dont_split = dont_split
        self.__dir = join(env.data_dir, self.key)

        if not exists(self.__dir):
            os.makedirs(self.__dir)

    def get_sets(self):
        train_path = join(self.__dir, 'train_ids.pickle')
        validate_path = join(self.__dir, 'validate_ids.pickle')
        test_path = join(self.__dir, 'test_ids.pickle')

        path = join(self.__dir, 'data.csv')
        if os.path.exists(path):
            with timer('load data:'):
                data = pandas.DataFrame.from_csv(path)
        else:
            data = self.get_data()
            data.to_csv(path)

        if exists(train_path) and exists(validate_path) and exists(test_path):
            train_ids = pickle.load(open(train_path, "rb"))
            validate_ids = pickle.load(open(validate_path, "rb"))
            test_ids = pickle.load(open(test_path, "rb"))
        else:
            if self.dont_split:
                
                ids = data[self.dont_split].drop_duplicates()
                test_size = len(ids) // 10
                train_ids, validate_ids = train_test_split(
                    ids,
                    test_size=test_size,
                    random_state=1
                )
                train_ids, test_ids = train_test_split(
                    train_ids,
                    test_size=test_size,
                    random_state=1
                )
                pickle.dump(train_ids, open(train_path, 'wb'))
                pickle.dump(validate_ids, open(validate_path, 'wb'))
                pickle.dump(test_ids, open(test_path, 'wb'))
                
            else:
                raise "Not Implemented"

        train = data.iloc[
            in1d(data[self.dont_split].values, train_ids.values)
        ]
        validate = data.iloc[
            in1d(data[self.dont_split].values, validate_ids.values)
        ]
        test = data.iloc[
            in1d(data[self.dont_split].values, test_ids.values)
        ]

        train = self.__class__.set(train)
        validate = self.__class__.set(validate, train.encoders)
        test = self.__class__.set(test, train.encoders)

        return train, validate, test
