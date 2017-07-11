import numpy as np
from collections import defaultdict


class FeatureSelectorBase(object):
    """Base class for feature selectors

    Attributes:
        apply_to (tuple[:class:`.FeatureBase`]): All the classes of
            features that this selector supports
        num_keep (int): How many features to keep per group
    """
    apply_to = None
    num_keep = None
    overlap_multiplier = .05
    min_size = None

    def __init__(self, verbose=False):
        self.verbose = verbose

    def select(self, feature_matrix, features, labels=None):
        """Selects best scoring features according to _score_groups

            Select averages each feature's score between all of the
            groups that contain it, and then increases the score by
            self.overlap_multiplier (default 5%) per group containing
            the feature beyond the first one.  Then groups are sorted in
            descending order based on their maximum feature score.  Each
            group selects self.num_keep features based on the Selector
            that created it.  Any features that were part of a group but
            not selected by any of them are deleted.


        Args:
            feature_matrix (np.array): calculated feature matrix for features
            features (list[:class:`.FeatureBase`]): list of features


        Returns:
            np.array: feature_matrix
            list[:class:`.FeatureBase`]: features

        Note:
            Modifies feature_matrix in place
        """
        features = list(features)  # make copy
        all_group_scores = self._make_groups(features, feature_matrix, labels)

        # average each feature's score across group
        summed_scores = defaultdict(list)
        for group_scores in all_group_scores:
            for f in group_scores.scores:
                summed_scores[f].append(group_scores.scores[f])

        # Multiply score for features that are in multiple groups
        for f in summed_scores:
            overlap = (1 + self.overlap_multiplier * len(summed_scores[f]))
            summed_scores[f] = \
                sum(summed_scores[f]) / len(summed_scores[f]) * overlap

        # Starting with groups that have best features, select the num_keep from each group
        selected = set([])
        sorted_groups = sorted(all_group_scores,
                               key=lambda g: -max([summed_scores[f]
                                                   for f in g.scores]))

        for feature_group in sorted_groups:
            # break ties by feature name
            keep = sorted(feature_group.scores,
                          key=lambda (k): (-summed_scores[k], k))[:feature_group.num_keep]

            selected = selected.union(keep)

        # Finally, delete features that weren't selected
        to_delete = [features.index(f) for f
                     in summed_scores if f not in selected]

        feature_matrix = np.delete(feature_matrix, to_delete, 1)

        if self.verbose:
            features_to_delete = [features[f] for f in to_delete]
            print "Removed %d features:" % (len(to_delete))
            print features_to_delete

        selected_features = \
            [f for i, f in enumerate(features) if i not in to_delete]

        return feature_matrix, selected_features

    def _make_groups(self, features, feature_matrix, labels):
        """Find and score groups of features"""
        feature_groups = self._find_groups(features)
        feature_groups = self._score_groups(feature_groups,
                                            feature_matrix, features, labels)
        return feature_groups

    def _find_groups(self, features):
        """Finds groups of related features"""
        assert self.apply_to is not None, "FeatureSelector subclasses " \
            "should instantiate apply_to"

        base_feature_groups = defaultdict(list)
        for x in [f for f in features if isinstance(f, self.apply_to)]:
            base_feature_groups[tuple(x.base_features)].append(x)

        return [SelectedGroup(self.num_keep, base_feature_groups[bf]) for bf
                in base_feature_groups.keys()
                if len(base_feature_groups[bf]) >= self.min_size]

    def _score_groups(self, feature_groups, feature_matrix, feature_list, labels):
        """Scores features in a a list of groups. gets scored based on variance"""
        scores = {}
        for group in feature_groups:
            for feature in group.scores:
                if feature not in scores:
                    try:
                        scores[feature] = \
                            abs(np.corrcoef(np.column_stack((feature_matrix[:,
                                                             feature_list.index(feature)],
                                                             labels)).astype(np.float64), rowvar=0)[0][1])
                    except:
                        a = np.column_stack((feature_matrix[:, feature_list.index(feature)],
                                            labels)).astype(np.float64)
                        print a
                        print a.dtype
                        raise Exception("Could not score a feature.  Check "
                                        "that the feature matrix is all "
                                        "numerical data and that categorical "
                                        "data is one-hot encoded")

                group.scores[feature] = scores[feature]

        return feature_groups


class SelectedGroup(object):

    def __init__(self, num_keep, scores):
        self.num_keep = num_keep
        if isinstance(scores, list):
            self.scores = {f: 0 for f in scores}
        else:
            self.scores = scores  # Dictionary of features and scores

    def __repr__(self):
        return str(self.scores) + " Keep:" + str(self.num_keep)
