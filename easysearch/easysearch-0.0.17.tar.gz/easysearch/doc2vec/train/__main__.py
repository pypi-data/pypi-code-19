import argparse

from easysearch.doc2vec.doc_similarity import DocumentSimilarity
from easysearch.utils import text


parser = argparse.ArgumentParser()
parser.add_argument('--collection')
parser.add_argument('--job_id')
parser.add_argument('--text_fields')
parser.add_argument('--host')
parser.add_argument('--port')
args = parser.parse_args()

collection = args.collection
print('collection', collection)
job_id = args.job_id
print('job_id', job_id)
text_fields = text.parse_text_args(args.text_fields)
print('text_fields', text_fields)
host = args.host
print('host', host)
port = args.port
print('port', port)

doc_similarity = DocumentSimilarity(collection=collection, job_id=job_id, text_fields=text_fields, easysearch_address=host, easysearch_port=port)
doc_similarity.train()
