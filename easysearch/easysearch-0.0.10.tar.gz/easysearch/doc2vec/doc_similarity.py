from gensim.models.doc2vec import Doc2Vec, TaggedDocument

#import time
import logging
import multiprocessing
import sys
import csv
csv.field_size_limit(sys.maxsize)

from easysearch.solr.solr_client import EasySearchSolrClient
from easysearch.utils import text, file


class DocumentSimilarity(object):

    def __init__(self, job_id, text_fields=None, collection='default', easysearch_address='localhost', easysearch_port='8080'):
        self.collection = collection
        self.job_id = job_id
        self.cores = multiprocessing.cpu_count()
        self.text_fields = text_fields
        self.easysearch_address = easysearch_address
        self.easysearch_port = easysearch_port
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

    def train(self):
        client = EasySearchSolrClient(collection=self.collection, text_fields=self.text_fields, base_addr=self.easysearch_address, port=self.easysearch_port)
        # Determina o total de documentos
        res = client.query_docs(job_id=self.job_id, rows=0)
        total = res.get_num_found()
        print(total, 'documents found')
        filename = self.save_documents_to_csv(solr_client=client, total_docs=total)
        # PV-DBOW
        model = Doc2Vec(dm=0, dbow_words=1, size=300, window=8, min_count=0, iter=50, workers=self.cores)
        documents = self.make_labeled_csv(filename=filename)
        model.build_vocab(documents)
        documents = self.make_labeled_csv(filename=filename)
        model.train(documents, total_examples=model.corpus_count, epochs=model.iter)
        model.save(self.get_model_name())

    def save_documents_to_csv(self, solr_client, total_docs, step=500):
        filename = self.get_csv_name()
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            start = 0
            rows = step
            end = rows
            for i in range(0, total_docs, step):
                if i == 0:
                    start = i
                    end = rows
                else:
                    start = i + 1
                    rows = step - 1
                    end = i + rows + 1
                res = solr_client.query_docs(job_id=self.job_id, start=start, rows=rows)
                for doc in res.docs:
                    try:
                        writer.writerow([doc['ctr_id'], ' '.join(text.get_text(doc, self.text_fields, min_len=1))])
                    except TypeError as error:
                        print(error)
                        print(doc['ctr_id'], 'was not written to ', filename)
                print('wrote files from', str(start), 'to', str(end))
        return filename

    def make_labeled_csv(self, filename):
        with open(filename) as f:
            r = csv.reader(f, delimiter=' ', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            try:
                for row in r:
                    yield TaggedDocument(row[1].split(), tags=[row[0]])
            except csv.Error as e:
                print('Erro ao processar linha do documento', row[0], ':', e)

    def get_model_name(self):
        return file.get_file_name(self.job_id, 'doc2vec', '_dbow.doc2vec')

    def get_csv_name(self):
        return file.get_file_name(self.job_id, 'doc2vec', '_processed.csv')

    def get_similar_documents(self, ctr_id, topn=10):
        model_name = self.get_model_name()
        #start_time = time.clock()
        model = Doc2Vec.load(model_name)
        model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
        #print(time.clock() - start_time)
        similars = model.docvecs.most_similar(positive=[ctr_id], topn=topn)
        similars = [similar[0] for similar in similars]
        print(similars)
        return similars
