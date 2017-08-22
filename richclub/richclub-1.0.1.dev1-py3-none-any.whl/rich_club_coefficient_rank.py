import networkx as nx
import pandas as pd



def rich_club_coefficient_rank(G):
    deg = G.degree()
    rich_club = []
    rich_club_coefficient = 0.0
    rank_deg =sorted(deg.items(), key=lambda d: d[1],reverse=True)
    for x in range(2,len(deg)+1):
        a = dict(rank_deg[:x])
        nodes = set(a)
        edges = 0
        for start_id, end_id in G.edges(nodes):
            if start_id in nodes:
                if end_id in nodes:
                    edges = edges + 1
        rich_club_coefficient = edges/((x*(x-1))/2) 
        if rich_club_coefficient != 0:
            rich_club.append((x,rich_club_coefficient))
    return rich_club