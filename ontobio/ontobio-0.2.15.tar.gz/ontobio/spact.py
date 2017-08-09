"""
Spreading activation
"""
import networkx as nx
import logging

class ActivationNetwork(object):

    def __init__(self, ontology=None, association_set=None):
        self.ontology = ontology
        self.association_set = association_set
        self.pseudocount = 1
        self.node_to_vname = {}
        self.vname_to_node = {}
        self.corpus_size = len(self.association_set.subjects)

    # TODO: cache
    def conditional_probability(self,c,a):
        """
        Returns
        -------
        float
            Pr(c|a) = |c^a|/|a|
        """
        aset = self.association_set
        ante_items = set(aset.query([a]))
        pc = self.pseudocount
        if c in aset.subjects:
            return (1+pc) / (len(ante_items) + pc)
        cons_items = set(aset.query([c]))
        # TODO: use disjointness axioms
        common_items = ante_items.intersection(cons_items)
        pr = (len(common_items) + pc) / (len(ante_items) + pc)
        return pr
    
    def probability(self,n):
        """
        Returns
        -------
        float
            Pr(n)
        """
        aset = self.association_set
        n_items = len(aset.query([n]))
        pc = self.pseudocount
        pr = (n_items + pc) / (self.corpus_size + pc)
        return pr

    def minimal_classifying_intersection(self, item):
        """
        For any given item (e.g. gene, disease), estimate the minimal set
        of classes whose intersection uniquely identify that item.
        """
        aset = self.association_set
        anns = aset.annotations(item)
        refitems = set(aset.subjects)
        done = False
        found = True
        ixn = []
        while not done:
            logging.debug("Finding additional classes; current={} bg={}".format(ixn,len(refitems)))
            pairs = []
            for a in anns:
                num = len(refitems.intersection(aset.query([a])))
                pairs.append( (num,a) )
            pairs.sort()
            logging.debug("BEST={}".format(pairs[0:5]))
            if len(pairs) > 0:
                cls_count,cls = pairs[0]
                ixn.append(cls)
                if cls_count > 1:
                    refitems = refitems.intersection(refitems.intersection(aset.query([cls])))
                    anns.remove(cls)
                else:
                    done = True
            else:
                done = True
                found = False
                
        return found, ixn

    # EXPERIMENTAL
    # For problog
    def node_vname(self, n):
        if n in self.node_to_vname:
            return self.node_to_vname[n]
        label = self.ontology.label(n)
        if label is None:
            label = 'leaf_' + self.association_set.label(n)
        import re
        vn = re.sub(r'\W+', '', label.replace(" ","_"))
        if re.match(r'^[0-9_]', vn):
            vn = 'x' + vn
        vn = vn.lower()
        self.node_to_vname[n] = vn
        if vn in self.vname_to_node:
            raise ValueError("Not unique: {} & {} = {}".format(n,self.vname_to_node,vn))
        self.node_to_vname[n] = vn
        return vn
    

    def write_rule(self, pr, h, b=[]):
        f = self.outfile
        #pr = str(pr)
        #if pr.startswith("."):
        #    pr = '0' + pr
        if len(b) == 0:
            f.write('% leaf\n')
            f.write('{} :: {}.\n'.format(pr,h))
        else:
            bstr = ', '.join(b)
            f.write('{} :: {} :- {}.\n'.format(pr,h,bstr))

    # EXPERIMENTAL
    def write_problog_bilayer(self, outfile):
        ont = self.ontology
        v2c = {}
        self.outfile = outfile
        
        false_positive = 0.05
        for c in ont.nodes():
            if ont.is_obsolete(c):
                continue
            v = self.node_vname(c)
            if v in v2c:
                raise ValueError("Not unique: {} & {} = {}".format(c,v2c[v],v))
            v2c[v] = c
            ov = 'obs_' + v

            # add rules. Always noisy-OR
            pas = ont.parents(c)
            chs = ont.children(c)
            if len(chs) == 0:
                pr = self.probability(c)
                if pr == 0.0:
                    pr = 0.0000001
                self.write_rule(pr, ov, [])
                
            for pa in pas:
                pav = self.node_vname(pa)

                # obs layer
                opav = 'obs_' + pav
                self.write_rule(1, opav, [ov])

                # layer 2
                pr = self.conditional_probability(c,pa)
                self.write_rule(pr, v, [pav])


            # bridge 
            self.write_rule(1-false_positive, v, [ov])
                
        aset = self.association_set
        for s in aset.subjects:
            v = self.node_vname(s)
            bvs = []
            for a in aset.annotations(s):
                pr = 0.5
                av = self.node_vname(a)
                bvs.append(av)
            self.write_rule(0.95, v, bvs)

    # EXPERIMENTAL
    def write_problog_simple(self, outfile):
        ont = self.ontology
        v2c = {}
        self.outfile = outfile

        def negate(v):
            return '\+'+v
        
        false_positive = 0.05
        for c in ont.nodes():
            if ont.is_obsolete(c):
                continue
            v = self.node_vname(c)
            if v in v2c:
                raise ValueError("Not unique: {} & {} = {}".format(c,v2c[v],v))
            v2c[v] = c

            # add rules. Always noisy-OR
            pas = ont.parents(c)
            if len(pas) == 0:
                self.write_rule(1.0, v, [])
                
            for pa in pas:
                pav = self.node_vname(pa)
                pr = self.conditional_probability(c,pa)
                self.write_rule(pr, v, [pav])
                self.write_rule(1, negate(v), [negate(pav)])
                
        aset = self.association_set
        for s in aset.subjects:
            v = self.node_vname(s)
            bvs = []
            for a in aset.annotations(s):
                pr = 0.5 # TODO - get this from metadata
                av = self.node_vname(a)
                fnv = v + '__' + av
                bvs.append(fnv)
                self.write_rule(1, fnv, [av])
                self.write_rule(1-pr, fnv, [negate(av)])
            self.write_rule(0.95, v, bvs)
            
    def _nodeset_ancestors(self, g, nodes):
        subnodes = set()
        for n in nodes:
            if n not in subnodes:
                subnodes.add(n)
                subnodes.update(nx.ancestors(g, n))
        return subnodes

    # TODO
    def tr_probability(self, source_weights, target_weights):
        """
        Arguments
        ---------
        source_weights : dict
            node to weight (prob) map
        target_weights : dict
            node to weight (prob) map
        """
        
        #wg = self.wnetwork()
        wg = self.ontology.get_graph()
        # TODO: check no cycles

        source_nodes = set(source_weights.keys())
        target_nodes = set(target_weights.keys())

        

        
        # only consider those in blanket
        # TODO: negative nodes should propagate down
        #subg = wg.subgraph(self._nodeset_ancestors(wg, source_nodes.union(target_nodes)))
        subg = wg.subgraph(self._nodeset_ancestors(wg, source_nodes))
        wm = self.propagate(subg, source_weights, True)

        for n in self._roots(wg):
            if n not in wm:
                wm[n] = self.probability(n)
        
        subg2 = wg.subgraph(self._nodeset_ancestors(wg, target_nodes))        
        wm = self.propagate(subg2, wm, False)

        # TODO: fold this in to propagate
        cum_pr = 1.0
        cum_neg_pr = 1.0        
        for n,w in target_weights.items():
            pr = wm[n] * w
            # TODO: use w
            logging.info(' PR({} {}) = {}'.format(n, self.ontology.label(n), pr))
            #cp = self.conditional_probability(,n)
            cum_pr *= pr
            cum_neg_pr *= ((1-pr) * w)
        return 1 - ((1-cum_pr) * cum_neg_pr)

    def _roots(self,g):
        return [n for n in g.nodes() if len(g.predecessors(n)) == 0 and len(g.successors(n)) > 0]
        

    # TODO
    def propagate(self, g, init_weights, up):
        """
        Arguments
        ---------
        weights : dict
            node to weight (prob) map
        up : bool
            True if weights to be propagated up, otherwise down
        """
        seeds = list(init_weights.keys())
        visited = set()
        weights = {}

        logging.info('**INIT {} SEEDS: {}'.format(up, seeds))
        while len(seeds) > 0:
            #logging.info('{} SEEDS: {}'.format(up, seeds))
            seed = seeds.pop()
            logging.debug('{} NEXT = {} {} // '.format(up, seed, self.ontology.label(seed), len(seeds)))
            if seed in visited:
                continue

            if seed not in g:
                logging.error("Seed {} not in g D={}".format(seed, up))
                continue
            
            pnodes = g.predecessors(seed)
            snodes = g.successors(seed)

            # set extension nodes plus antecedent nodes
            if up:
                dnodes = snodes
                xnodes = pnodes
            else:
                dnodes = pnodes
                xnodes = snodes

            xnodes = [x for x in xnodes if x not in visited and x not in seeds]
            #logging.info('XNODES({} {}) = {}'.format(seed, self.ontology.label(seed), xnodes))
            visited.add(seed)
            seeds += xnodes
            
            if seed in init_weights:
                weights[seed] = init_weights[seed]
                continue

            has_all_deps = True
            for n in dnodes:
                if n not in weights:
                    # TODO: this ends up propagating down to everything
                    seeds = [n,seed] + seeds
                    has_all_deps = False
                    break
            if not has_all_deps:
                visited.remove(seed)
                continue
                
            # noisy-OR
            cum_neg_pr = 1.0
            for n in dnodes:
                pr_n = weights[n]
                cp = self.conditional_probability(seed,n)
                ppr = cp * pr_n
                #logging.info("     CP({}|{}) = {}  ppr={}".format(seed,n,cp,ppr))
                cum_neg_pr *= (1-ppr)
            pr = 1-cum_neg_pr
            weights[seed]= pr
            logging.debug('{} pr({} {}) = {}'.format(up, seed, self.ontology.label(seed), pr))
            
        return weights
        
