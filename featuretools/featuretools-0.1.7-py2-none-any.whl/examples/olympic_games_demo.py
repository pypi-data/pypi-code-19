import cPickle as pck
import pandas as pd
import numpy as np
import gc
from sklearn.preprocessing import Imputer, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import featuretools as ft
from featuretools import primitives as ftypes
from featuretools.selection.variance_selection import (plot_feature_variances,
                                                       select_high_variance_features)
from featuretools.examples.olympic_games_utils import (load_entityset,
                                                       MostNumerousByGroup,
                                                       MostNumerousGroup,
                                                       set_use_previous,
                                                       bin_labels,
                                                       CustomTimeSeriesSplit,
                                                       get_feature_importances)

es = load_entityset()
es


# Define Features

# Custom seed features
medals_country = ft.Feature(es['athletes']['Country'], es['medals'])
is_gold = ft.Feature(es['medals']['Medal']) == 'Gold'
olympic_id = ft.Feature(es['medals']['Olympic ID'])
country_with_most_golds = MostNumerousGroup(es['medals']['medal_id'],
                                            medals_country,
                                            es['olympics'],
                                            where=is_gold).rename("country_with_most_golds_won")
most_golds_won = MostNumerousByGroup(es['medals']['medal_id'],
                                     medals_country,
                                     es['olympics'],
                                     where=is_gold).rename("most_golds_won")
# Connect to medals (since olympics is too far away from countries @ max_depth=2)
most_golds_won_in_medals = ft.Feature(most_golds_won, es['medals'])
country_with_most_golds_in_medals = ft.Feature(country_with_most_golds, es['medals'])
agg_primitives = [ftypes.Sum, ftypes.Std, ftypes.Max,
                  ftypes.Min, ftypes.Mean, ftypes.Count,
                  ftypes.PercentTrue, ftypes.NUnique, ftypes.Mode,
                  ftypes.Trend]
# Run DFS
# We split into two steps so that we can set the use_previous flag of some auto-generated features
features = ft.dfs(entityset=es,
                  target_entity="countries",
                  trans_primitives=[],
                  agg_primitives=agg_primitives,
                  max_depth=2,
                  seed_features=[country_with_most_golds_in_medals, most_golds_won_in_medals],
                  features_only=True,
                  verbose=True)

# Set use previous
features_last_4_years = set_use_previous(features, '4 years')


# Load labels and cutoff times
label_df = pd.read_csv("/Users/bschreck/olympic_games_data/num_medals_by_country_labels.csv", parse_dates=['olympics_date'],
                       encoding='utf-8')
cutoff_times = label_df[['country', 'olympics_date']].rename(columns={'country': 'instance_id', 'olympics_date': 'time'})
cutoff_times.shape


# Calculate feature matrix
feature_matrix = ft.calculate_feature_matrix(features_last_4_years,
                                             cutoff_time=cutoff_times,
                                             verbose=True)


# Save our work
fm_file = "/Users/bschreck/olympic_games_data/feature_matrix_by_country.p"
feature_matrix.to_pickle(fm_file)
features_file = "/Users/bschreck/olympic_games_data/features_by_country.p"
with open(features_file, 'wb') as f:
    pck.dump(features_last_4_years, f)
# hv_fm = pd.read_pickle(fm_file)


# Select features with high variance
variances = plot_feature_variances(feature_matrix, features, log_plot=False)
len(variances[variances > 10])
hv_fm, hv_f = select_high_variance_features(feature_matrix, features, threshold=10, categorical_nunique_ratio=.1)

# One-hot-encode categorical features
feature_matrix_encoded, features_encoded = ft.encode_features(hv_fm, hv_f)



# Save our work
fm_file = "/Users/bschreck/olympic_games_data/feature_matrix_hv_by_country.p"
# hv_fm.to_pickle(fm_file)
features_file = "/Users/bschreck/olympic_games_data/features_hv_by_country.p"
# with open(features_file, 'wb') as f:
#           pck.dump(hv_f, f)
with open(features_file, 'rb') as f:
    hv_f = pck.load(f)
hv_fm = pd.read_pickle(fm_file)


# In[ ]:


# Binarize and bin labels
labels = label_df['num_medals']
binned_labels, bins = bin_labels(labels, [2, 6])
binned_labels.value_counts()
binary_labels = labels >= 2


# Create scikit-learn estimator

# Note: increasing estimators from 50 to 400 does not change output
estimator = Pipeline([("imputer", Imputer(missing_values='NaN',
                                          strategy="most_frequent",
                                          axis=0)),
                      ("scaler", RobustScaler(with_centering=True)),
                      ("rf", RandomForestClassifier(n_estimators=50, class_weight='balanced', n_jobs=-1))])



# Use a custom splitter that makes sure the set of labels for each unique Olympic Games
# is in the same group
splitter = CustomTimeSeriesSplit(label_df['olympics_date'], n_splits=5)
binned_score = cross_val_score(estimator, feature_matrix_encoded.values, binned_labels.values, scoring='f1_macro', verbose=1,
                               cv=splitter)
binned_score = [max(s, 1 - s) for s in binned_score]
print "Binned scores: ", binned_score
print "Binned mean score: %.2f +/- %.2f" % (np.mean(binned_score), np.std(binned_score))

score = cross_val_score(estimator, feature_matrix_encoded.values, binary_labels.values,
                        scoring='roc_auc', verbose=1,
                        cv=splitter)

score = [max(s, 1 - s) for s in score]
print "Scores: ", score
print "Mean score: %.2f +/- %.2f" % (np.mean(score), np.std(score))


# Train on all data and get importances
binned_feature_imps_by_time, dates = get_feature_importances(estimator, feature_matrix_encoded, binned_labels, splitter)
feature_imps_by_time, dates = get_feature_importances(estimator, feature_matrix_encoded, binary_labels, splitter)

for i, fi in enumerate(binned_feature_imps_by_time):
    train_dates, test_dates = dates[i]
    train_years = [td.year for td in train_dates]
    test_years = [td.year for td in test_dates]
    print "Train years: %s" % train_years
    print "Test years: %s" % test_years
    print "Top 10 feats:"
    for f in fi.index[:100]:
        print "   ", f


# Let's try only using games after 1960, because we only have economic data since then.
# # TODO: without Population or GDP from static countries file

# We'll try the previous 8 years this time

# FYI: I kept running out of memory on my 4GB macbook pro
del feature_matrix_encoded
del hv_fm
del feature_matrix
gc.collect()

encoded_hv_features_last_8_years = set_use_previous(features_encoded, '8 years')
# Only use instances after 1960
cutoff_times_since_1960 = cutoff_times[cutoff_times['time'] >= pd.Timestamp('1/1/1960')]
fm_since_1960 = ft.calculate_feature_matrix(encoded_hv_features_last_8_years,
                                            cutoff_time=cutoff_times_since_1960,
                                            verbose=True)


# Get labels after 1960 and binarize as well
labels = label_df['num_medals'][label_df['time'] >= pd.Timestamp('1/1/1960')]
binary_labels = labels >= 2
feature_imps_since_1960, dates = get_feature_importances(estimator, fm_since_1960, binary_labels, splitter)


# Part 2: make use_previous 8 or more  years, and predict GDP or other economic indicator
