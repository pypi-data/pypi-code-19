from featuretools.variable_types.variable import Categorical
import pandas as pd


def encode_features(features, feature_matrix, top_n=10, include_unknown=True, inplace=False):
    """Encode categorical features

        Args:
            features (list[:class:`.FeatureBase`]): Feature definitions in feature_matrix
            feature_matrix (pd.DataFrame): Dataframe of features
            top_n (pd.DataFrame): number of top values to include
            include_unknown (pd.DataFrame): add feature encoding an unkwown class.
                defaults to True
            inplace (bool): encode feature_matrix in place. Defaults to False.

        Returns:
            (list, pd.Dataframe) : encoded features, encoded feature_matrix

        Example:
            .. ipython:: python
                :suppress:

                from featuretools.tests.testing_utils import make_ecommerce_entityset
                from featuretools.primitives import Feature
                import featuretools as ft
                es = make_ecommerce_entityset()

            .. ipython:: python

                f1 = Feature(es["log"]["product_id"])
                f2 = Feature(es["log"]["purchased"])
                f3 = Feature(es["log"]["value"])

                features = [f1, f2, f3]
                ids = [0, 1, 2, 3, 4, 5]
                feature_matrix = ft.calculate_feature_matrix(features,
                                                             instance_ids=ids)

                f_encoded, fm_encoded = ft.encode_features(features,
                                                           feature_matrix)
                f_encoded

                f_encoded, fm_encoded = ft.encode_features(features,
                                                           feature_matrix, top_n=2)
                f_encoded

                f_encoded, fm_encoded = ft.encode_features(features, feature_matrix,
                                                           include_unknown=False)
                f_encoded

                f_encoded, fm_encoded = ft.encode_features(features, features_matrix,
                                                           to_encode=['purchased'])
                f_encoded
    """
    if inplace:
        X = feature_matrix
    else:
        X = feature_matrix.copy()

    encoded = []
    for f in features:
        if not f.variable_type == Categorical:
            encoded.append(f)
            continue

        unique = X[f.get_name()].value_counts().head(top_n).index.tolist()
        for label in unique:
            add = f == label
            encoded.append(add)
            X[add.get_name()] = (X[f.get_name()] == label).astype(int)

        if include_unknown:
            unknown = f.isin(unique).NOT().rename(f.get_name() + " = unknown")
            encoded.append(unknown)
            X[unknown.get_name()] = (~X[f.get_name()].isin(unique)).astype(int)

        X.drop(f.get_name(), axis=1, inplace=True)

    new_X = X[[e.get_name() for e in encoded]]
    for c in new_X:
        try:
            new_X[c] = pd.to_numeric(new_X[c], errors='raise')
        except (TypeError, ValueError):
            pass
    return encoded, new_X
