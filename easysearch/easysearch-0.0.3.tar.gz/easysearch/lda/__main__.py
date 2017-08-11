import argparse

from easysearch.lda.lda_similarity import LdaSimilarity
from easysearch.utils import text


parser = argparse.ArgumentParser()
parser.add_argument('--job_id')
parser.add_argument('--documents')
args = parser.parse_args()

job_id = args.job_id
print('job_id', job_id)
documents = text.parse_text_args(args.documents)
print('documents', documents)

lda_similarity = LdaSimilarity(job_id=job_id)
lda_similarity.get_clusters_info(texts=documents)
