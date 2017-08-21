import ontobio.ontol

class babelify(object):

    def __init__(self,ontology):
        self.ontology=ontology
        self.N = 4

    def babelify(self):
        ont = self.ontology

        onts = []
        for i in range(0,self.N):
            onts.append(ontol.Ontology())
        for cls in ont.nodes():
            label = ont.label(cls)
            if label is None:
                continue
            for i in range(0,self.N):
                ontc = onts[i]
                g = ontc.get_graph()
                n2 = self.clone_node_id(cls, i)
                label2 = self.clone_label(label, i)
                g.add_node(n2, {'label': label2})
                
