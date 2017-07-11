from .feature_selector import FeatureSelectorBase, SelectedGroup
from featuretools.features import FeatureBase
from featuretools.backend.utils.bootstrap_estimation import bootstrap, bag_of_little_bootstraps
from featuretools.variable_types.variable import Categorical
from collections import defaultdict
import numpy as np
import pandas as pd
from numpy.random import RandomState


class CorrelationSelector(FeatureSelectorBase):
    """Removes redundant features by measuring how closely features are
        correlated"""

    apply_to = (FeatureBase)
    num_keep = 1
    min_size = 2

    def __init__(self, verbose=False, threshhold=.95,
                 bootstrap_min_instances=1000, blb_min_instances=5000,
                 sample_seed=None):
        """

        Args:
            verbose (bool, optional): prints output

            threshhold (float, optional): minimum correlation between a
                set of features to consider them a group

            bootstrap_min_instances (int, optional): minimum number of
                instances to use bootstrap on.  If less uses plain
                correlation

            blb_min_instances (int, optional): minimum number of
                instances to use bag of little bootstraps on.  If less
                uses bootstrap or plain correlation

            sample_seed (int, optional): seed for the PRNGs
        """
        super(self.__class__, self).__init__(verbose)
        self.threshhold = threshhold
        self.bootstrap_min_instances = bootstrap_min_instances
        self.blb_min_instances = blb_min_instances
        self.sample_seed = sample_seed
        if sample_seed is None:
            self.sampler = RandomState()
        else:
            self.sampler = RandomState(sample_seed)

    def _make_groups(self, features, feature_matrix, labels):
        """Find and score groups of features"""

        feature_groups = self._find_groups(features, feature_matrix)
        feature_groups = self._score_groups(feature_groups, feature_matrix,
                                            features, labels)

        return feature_groups

    def _find_groups(self, features, feature_matrix):
        """Finds all groups of features where the correlation between
            any two features is less than the threshhold

        Args:
            features (list[:class:`FeatureBase`]): list of features
            feature_matrix (np.ndarray): calculated feature matrix for features

        Returns:
            list: returns a list of unscored SelectedGroups
        """
        corr_grid = self._calc_correlation_grid(feature_matrix, features)
        correlated_features = defaultdict(list)
        for row in range(corr_grid.shape[0]):
            for col in range(corr_grid.shape[1]):
                # Note that the corr_grid rows are ordered backwards

                val = corr_grid.iloc[row, col]
                if val is None:
                    continue

                if np.isnan(val):
                    corr_grid.iloc[row, col] = None
                    continue

                if abs(val) > self.threshhold:
                    self._append_feature_to_group(correlated_features, row,
                                                  col, corr_grid)

        return_groups = []
        for key_feature in correlated_features:
            for correlated_group in correlated_features[key_feature]:

                correlated_group.add(key_feature)
                return_groups.append(SelectedGroup(self.num_keep,
                                                   [features[x] for x
                                                    in correlated_group]))

        return return_groups

    def _calc_correlation_grid(self, feature_matrix, features):
        """Calculates a matrix showing the correlation between any two
            features

        Args:
            feature_matrix (np.ndarray): calculated feature matrix for features
            features (list[:class:`FeatureBase`]): list of features

        Returns:
            pd.DataFrame: table where corr_grid[i][j] is the correlation
                between feature i and j
        """
        ignore_types = [Categorical]
        all_rows = []
        for i, feature_1 in enumerate(features):

            row = [None] * (i + 1)
            for j, feature_2 in enumerate(features[i + 1:], start=(i + 1)):

                feature_2 = features[j]
                if feature_1.variable_type in \
                        ignore_types or feature_2.variable_type in ignore_types:
                    row.append(None)

                else:
                    result = self._calc_correlation(feature_matrix, i, j)
                    row.append(result)

            all_rows.append(row)

        return pd.DataFrame(all_rows)

    def _calc_correlation(self, feature_matrix, i, j):
        """Calculates the correlation between two features using plain
            correlation, bootstrap, or bag of little bootstraps
            depending on the size of the feature matrix

        Args:
            feature_matrix (np.ndarray):
            i (int): index of the first feature
            j (int): index of the second feature

        Returns:
            int: correlation of the two features
        """
        def _metric_func(df):
            return np.corrcoef(df.astype(np.float64), rowvar=0)[0][1]

        if feature_matrix.shape[0] < self.bootstrap_min_instances:
            need_bootstrap = False

        elif feature_matrix.shape[0] < self.blb_min_instances:
            corr = bootstrap
            parameters = (4, feature_matrix.shape[0] / 10, _metric_func,
                          self.sample_seed, self.sampler)
            need_bootstrap = True

        else:
            corr = bag_of_little_bootstraps
            parameters = (4, 30, feature_matrix.shape[0] / 20, _metric_func,
                          self.sample_seed, self.sampler)
            need_bootstrap = True

        if need_bootstrap:
            num_samples = max(feature_matrix.shape[0] / 10,
                              self.bootstrap_min_instances)
            # Seperate just the two columns
            matrix_subset = np.column_stack((feature_matrix[:, i],
                                            feature_matrix[:, j]))

            # Take num_samples rows from sub_matrix
            sampled_matrix = matrix_subset[self.sampler.choice(np.arange(
                feature_matrix.shape[0]), num_samples)]

            # Averages the bootstrap or BLB results
            return np.nanmean(corr(sampled_matrix, *parameters))

        else:
            return np.corrcoef(feature_matrix[:, i].astype(np.float64),
                               feature_matrix[:, j].astype(np.float64),
                               rowvar=0)[0][1]

    def _append_feature_to_group(self, correlation_dict, key_feature,
                                 correlated_feature, corr_grid):
        """Once correlated_feature has been determined to be correlated


        Args:
            correlation_dict (dict): All of the correlated features
            key_feature (:class:`FeatureBase`): earlier correlated feature
            correlated_feature (:class:`FeatureBase`): later correlated feature
            corr_grid (pd.DataFrame): table of the correlation between each
                pair of features

        Returns:
            None: modifies the correlation_dict
        """
        sets = correlation_dict[key_feature]

        if len(sets) == 0:
            correlation_dict[key_feature] = [set([correlated_feature])]
            return

        correlated_features = set([])
        for group in sets:
            for index in group:

                if abs(corr_grid.iloc[key_feature, index]) > self.threshhold:
                    correlated_features.add(index)

        for index in correlated_features:
                corr_grid.iloc[index, correlated_feature] = np.nan

        if correlated_features in sets:
            group = sets[sets.index(correlated_features)]
            group.add(correlated_feature)

        else:
            correlated_features.add(correlated_feature)
            sets.append(correlated_features)
