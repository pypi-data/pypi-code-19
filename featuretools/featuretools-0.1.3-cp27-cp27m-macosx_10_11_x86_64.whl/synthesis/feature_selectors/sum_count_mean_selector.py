from .feature_selector import FeatureSelectorBase, SelectedGroup
from featuretools.features import Count, Mean, Sum
from collections import defaultdict


class SumCountMeanSelector(FeatureSelectorBase):
    apply_to = (Count, Mean, Sum)
    num_keep = 2
    min_size = 3

    def _find_groups(self, features):
        assert self.apply_to is not None
        features = [f for f in features if isinstance(f, self.apply_to)]

        # group features by their base feature
        groups = defaultdict(list)
        for f in features:
            if isinstance(f, Count):
                continue
            groups[tuple(f.base_features)].append(f)

        # find and add Counts to groups
        counts = {f.child_entity.id: f for f in features if isinstance(f, Count)}
        for base_features in groups:
            if base_features[0].entity.id in counts:
                count_feat = counts[base_features[0].entity.id]
                groups[base_features].append(count_feat)

        return [SelectedGroup(self.num_keep, groups[bf]) for bf in groups]
