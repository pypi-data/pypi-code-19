from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.models.phrases import Phraser

import logging
import multiprocessing

from easysearch.solr.solr_client import EasySearchSolrClient
from easysearch.utils import text, file


class LdaSimilarity(object):

    def __init__(self, job_id, collection='default', easysearch_address='localhost', easysearch_port='8080'):
        self.collection = collection
        self.job_id = job_id
        self.cores = multiprocessing.cpu_count()
        self.easysearch_address = easysearch_address
        self.easysearch_port = easysearch_port
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

    def train(self, num_topics=100, passes=10, chunksize=1000):
        client = EasySearchSolrClient(collection=self.collection, base_addr=self.easysearch_address, port=self.easysearch_port)
        # Consulta os documentos
        res = client.query_docs(job_id=self.job_id, rows=0)
        total = res.get_num_found()
        print(total, 'documents found')
        res = client.query_docs(job_id=self.job_id, rows=total)
        # Processa os documentos para treino
        train_texts, phraser = text.process_texts_for_lda(docs=res.docs, text_fields=['ctr_content_nlp'])
        phraser.save(self.get_phraser_name())
        dictionary = Dictionary(train_texts)
        # Filtra palavras que ocorrem em menos de 5 documentos ou que ocorrem em mais de 50% dos documentos.
        dictionary.filter_extremes(no_below=5, no_above=0.5)
        dictionary.save(self.get_dictionary_name())
        corpus = [dictionary.doc2bow(text) for text in train_texts]
        # Aqui estão sendo usados 30 tópicos, mas este valor deve ser determinado anteriormente, com base nos documentos do cliente
        model = LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary, chunksize=chunksize, passes=passes, \
                         iterations=400, eval_every=1, eta='auto', alpha='auto')
        model.save(self.get_model_name())

    def get_model_name(self):
        return file.get_file_name(self.job_id, 'lda', '_topics.lda')

    def get_dictionary_name(self):
        return file.get_file_name(self.job_id, 'lda', '.dict')

    def get_phraser_name(self):
        return file.get_file_name(self.job_id, 'lda', '.phraser')

    def normalize_word_topic(self, word_from_topic):
        if '_' in word_from_topic:
            words = word_from_topic.split('_')
            if words[0] == words[1]:
                return words[0]
            else:
                return ' '.join(words)
        else:
            return word_from_topic

    def get_clusters_info(self, documents):
        client = EasySearchSolrClient(collection=self.collection, base_addr=self.easysearch_address, port=self.easysearch_port)
        texts = []
        for ctr_id in documents:
            doc = client.query_doc(ctr_id=ctr_id)
            texts.append(doc['ctr_content_nlp'])
        return self.get_clusters_info_for_texts(texts=texts)

    def get_clusters_info_for_texts(self, texts):
        # Processa o texto para obtenção do bag of words do dicionário
        phraser_name = self.get_phraser_name()
        phraser = Phraser.load(phraser_name)
        # Obtém o bag of words a partir do dicionário
        dict_name = self.get_dictionary_name()
        dictionary = Dictionary.load(dict_name)
        # Carrega o modelo LDA para obtenção dos tópicos
        model_name = self.get_model_name()
        model = LdaModel.load(model_name)
        result = []
        # Os topics retornados aqui são tuplas de valores (tópico, score do documento no tópico)
        for text in texts:
            result.append(self.get_cluster_info(phraser=phraser, dictionary=dictionary, model=model, document_text=text))
        print(result)
        return result

    def get_cluster_info(self, phraser, dictionary, model, document_text):
        # Processa o texto para obtenção do bag of words do dicionário
        lda_text = text.process_text_for_lda(text=document_text, phraser=phraser)
        # Obtém o bag of words a partir do dicionário
        bow = dictionary.doc2bow(lda_text)
        # Os topics retornados aqui são tuplas de valores (tópico, score do documento no tópico)
        topics_scores = model[bow]
        best_topic = max(topics_scores, key=lambda topic_score:topic_score[1])
        topic = model.show_topic(best_topic[0])
        return [self.normalize_word_topic(word_probability[0]) for word_probability in topic]
