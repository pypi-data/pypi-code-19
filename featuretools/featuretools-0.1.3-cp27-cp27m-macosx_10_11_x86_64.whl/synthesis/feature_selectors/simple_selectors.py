from .feature_selector import FeatureSelectorBase
from featuretools.features import Min, Max, Mean


class MinMaxMeanSelector(FeatureSelectorBase):
    # This is now basically just an underpowered version of the correlation selector
    apply_to = (Min, Mean, Max)
    num_keep = 2
    min_size = 2
