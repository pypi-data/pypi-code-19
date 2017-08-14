import argparse

from easysearch.lda.lda_similarity import LdaSimilarity

parser = argparse.ArgumentParser()
parser.add_argument('--collection')
parser.add_argument('--job_id')
parser.add_argument('--num_topics')
parser.add_argument('--passes')
parser.add_argument('--chunksize')
parser.add_argument('--host')
parser.add_argument('--port')
args = parser.parse_args()

collection = args.collection
print('collection', collection)
job_id = args.job_id
print('job_id', job_id)
num_topics = int(args.num_topics)
print('num_topics', num_topics)
passes = int(args.passes)
print('passes', passes)
chunksize = int(args.chunksize)
print('chunksize', chunksize)
host = args.host
print('host', host)
port = args.port
print('port', port)


lda_similarity = LdaSimilarity(collection=collection, job_id=job_id, easysearch_address=host, easysearch_port='8080')
lda_similarity.train(num_topics=num_topics, passes=passes, chunksize=chunksize)
