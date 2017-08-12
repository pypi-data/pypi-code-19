import argparse

from easysearch.doc2vec.doc_similarity import DocumentSimilarity


parser = argparse.ArgumentParser()
parser.add_argument('--job_id')
parser.add_argument('--ctr_id')
parser.add_argument('--topn')
args = parser.parse_args()

job_id = args.job_id
print('job_id', job_id)
ctr_id = args.ctr_id
print('ctr_id', ctr_id)
topn = int(args.topn)
print('topn', topn)

doc_similarity = DocumentSimilarity(job_id=job_id)
doc_similarity.get_similar_documents(ctr_id=ctr_id, topn=topn)
