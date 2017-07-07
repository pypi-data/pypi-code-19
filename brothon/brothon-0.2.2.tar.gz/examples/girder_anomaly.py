"""Anomaly Detection Example"""
from __future__ import print_function

import sys

# Third Party Imports
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

# Local imports
from brothon import bro_log_reader
from brothon.analysis import dataframe_to_matrix

# Get the handle to the log
bro_log = log

# Example to show the dataframe cache functionality on streaming data
pd.set_option('display.width', 200)

print('Opening Data File: {:s}'.format(bro_log))
reader = bro_log_reader.BroLogReader(bro_log)

# Create a Pandas dataframe from reader
bro_df = pd.DataFrame(reader.readrows())
print('Read in {:d} Rows...'.format(len(bro_df)))
print(bro_df.columns.tolist())

# Sanity check either http or dns log
if 'request_body_len' in bro_df.columns.tolist():
    log_type = 'http'
    features = ['id.resp_p', 'method', 'resp_mime_types', 'request_body_len']
elif 'Z' in bro_df.columns.tolist():
    log_type = 'dns'
    features = ['Z', 'rejected', 'proto', 'query', 'qclass_name', 'qtype_name', 'rcode_name', 'query_length']
else:
    print('This example only works with Bro with http.log or dns.log files..')
    sys.exit(1)

# Create a Bro IDS log reader
# Using Pandas we can easily and efficiently compute additional data metrics
# Here we use the vectorized operations of Pandas/Numpy to compute query length
if log_type == 'dns':
    bro_df['query_length'] = bro_df['query'].str.len()

# Use the BroThon DataframeToMatrix class
to_matrix = dataframe_to_matrix.DataFrameToMatrix()
bro_matrix = to_matrix.fit_transform(bro_df[features])
print(bro_matrix.shape)

# Train/fit and Predict anomalous instances using the Isolation Forest model
odd_clf = IsolationForest(contamination=0.20)
odd_clf.fit(bro_matrix)

# Now we create a new dataframe using the prediction from our classifier
odd_df = bro_df[features][odd_clf.predict(bro_matrix) == -1]

# Now we're going to explore our odd observations with help from KMeans
odd_matrix = to_matrix.fit_transform(odd_df)
num_clusters = min(len(odd_df), 4) # 4 clusters unless we have less than 10 observations
odd_df['cluster'] = KMeans(n_clusters=num_clusters).fit_predict(odd_matrix)
print(odd_matrix.shape)

# Now group the dataframe by cluster
cluster_groups = odd_df[features+['cluster']].groupby('cluster')

# Now print out the details for each cluster
print('<<< Outliers Detected! >>>')
for key, group in cluster_groups:
    print()
    print('Cluster {:d}: {:d} observations'.format(key, len(group)))
    print(group.head(20))

