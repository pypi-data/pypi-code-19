from SolrClient import SolrClient


class EasySearchSolrClient(object):

    def __init__(self, base_addr='localhost', port='8080', collection='default', text_fields=['api_Arquivo_bn','api_Visualizar_bv']):
        self.baseAddr = base_addr
        self.port = port
        self.collection = collection
        self.text_fields = text_fields

    def query_docs(self, job_id, start=0,rows=1000):
        solr = SolrClient(self.getSolrAddress())
        field_list = ['ctr_id', 'ctr_content_nlp']
        field_list.extend(self.text_fields)
        query_def = {
                    'q': '*:*',
                    'indent': 'true',
                    'fl': ','.join(field_list),
                    'fq': '(-ctr_id:id_document_spell AND api_ɉȏɓɨɗ_st:' + job_id + ')',
                    'wt': 'json',
                    'charset': 'utf-8',
                    'start': str(start),
                    'rows': str(rows)
                    }
        return solr.query(self.collection, query_def)

    def query_doc(self, ctr_id, field_list=[]):
        solr = SolrClient(self.getSolrAddress())
        field_list.extend(['ctr_id', 'ctr_content_nlp'])
        query_def = {
                    'q': '*:*',
                    'fq': '(ctr_id:' + ctr_id + ')',
                    'indent': 'true',
                    'fl': ','.join(field_list),
                    'wt': 'json',
                    'charset': 'utf-8'
                    }
        res = solr.query(self.collection, query_def)
        if len(res.docs) > 0:
            return res.docs[0]

    def getSolrAddress(self):
        address = 'http://' + self.baseAddr + ':' + self.port
        if self.port != '8983':
            # Não é desenv, não precisa do /easysearch
            address = address + '/easysearch'
        return address