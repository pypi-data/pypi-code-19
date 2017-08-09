class OboGen():

    def _tag(self, tag, obj, k=None):
        if k is None:
            t = tag
        if k in obj:
            return "{}: {}\n".format(tag,obj[k])
        else:
            return ""
        
    def render_header(self, meta):
        s = "ontology: test\n";
        s += "\n"
        
    def render_entity(self, obj):
        """
        Renders an entity object (e.g. gene, gene product) as obo format.

        We follow a simple model compatible with Neo, PRO, etc.

        - Each entity is a class
        - use in_taxon for taxon
        """
        s = "[Term]\n"
        s += self._tag('id', obj)
        s += self._tag('name', obj, 'label')
        for s in obj['synonyms']:
            s += "synonym: \"{}\" RELATED []\n".format(s)
        if 'taxon' in obj:
            s += "relationship: in_taxon {}\n".format(obj['taxon'])
        s += "\n"

    def render_footer(self, meta):
        pass # TODO: in-taxon

    def write(self):
        pass
