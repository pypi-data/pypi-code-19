import networkx as nx
import glob

__author__ = 'rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"

for file in glob.glob("results/1000_1000_15_0.7_0.8_0.3_1/graph-*"):

    g = nx.read_edgelist(file, delimiter="\t")
    cms = file.replace("graph", "communities")
    f = open(cms)
    c = 0
    for l in f:
        nodes = map(int, l.strip().replace("]", "").split("[")[1].replace(" ", "").split(","))
        s = nx.subgraph(g, nodes)
        if nx.number_connected_components(s) > 1:
            print "ERRORE"
        c+=1

    print file, nx.number_connected_components(g), c, nx.number_of_nodes(g)
