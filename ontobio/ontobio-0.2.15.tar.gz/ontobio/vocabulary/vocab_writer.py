from prefixcommons.curie_util import expand_uri
import re
import logging

class VocabWriter(object):

    def __init__(self,
                 ontology=None,
                 use_curies=True,
                 use_labels=True):
        self.ontology = ontology
        self.use_curies = use_curies
        self.use_labels = use_labels
    
    def codegen(self, cls_name, supercls_name='object'):
        ont = self.ontology
        s = "class {}({}):\n".format(cls_name, supercls_name)
        for p in ont.nodes():
            if True or ont.get_node_type(p) == 'PROPERTY':
                p_uri = p
                if not self.use_curies:
                    p_uri = expand_uri(p)
                p_var = None
                if self.use_labels:
                    p_var = ont.label(p)
                else:
                    p_var = p.replace(":","_")
                if p_var is None:
                    logging.warn("Skipping: {}".format(p))
                    continue
                
                p_var = p_var.replace(" ","_")
                p_var = re.sub('[^0-9a-zA-Z_]+', '', p_var)

                # some vars may start with a number
                if re.match("^[0-9]",p_var) is not None:
                    p_var = '_' + p_var

                s += "    {} = '{}'\n".format(p_var, p_uri)
        s += "\n"
        return s



            
        
