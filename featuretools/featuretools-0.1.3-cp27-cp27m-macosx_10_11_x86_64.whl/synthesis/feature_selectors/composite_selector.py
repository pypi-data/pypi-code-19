from .feature_selector import FeatureSelectorBase


class CompositeSelector(FeatureSelectorBase):

    def __init__(self, selectors, verbose=False):
        """Summary

        Args:
            selectors (list[:class:`FeatureSelectorBase`]): list of
                feature selectors to generate scores
        """
        super(self.__class__, self).__init__(verbose)
        self.selectors = selectors

    def _make_groups(self, features, feature_matrix, labels=None):
        scores = []
        for selector in self.selectors:
            scores.extend(selector._make_groups(features,
                                                feature_matrix, labels))
        return scores
