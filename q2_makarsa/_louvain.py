import community as community_louvain
import networkx as nx
import pandas as pd
import numpy as np
from netneurotools import cluster
from ._network import NetworkDirectoryFormat

def louvain_communities (
                        network_input: NetworkDirectoryFormat,
                        num_partitions: int = 100,
                        remove_neg: bool = False,
                        seed: int = None, 
                        )->pd.DataFrame:
    #load data and create network graph
    
    G = nx.read_graphml("/".join([str(network_input), "network.graphml"]))

    def remove_negative_edges(G):
        #Remove the negative edges from the graph 
        G_new = nx.Graph()
        G_new.add_nodes_from(G.nodes())
        for u, v, weight in G.edges(data='weight'):
            if weight >= 0:
                G_new.add_edge(u, v, weight=weight)
        return G_new
    
    #Get absolute weights of the graph
    def absolute_value_edges(G):
        for u, v, data in G.edges(data=True):
            data['weight'] = abs(data['weight'])
        return G

    if remove_neg==True:
        otu_graph = remove_negative_edges(G)
    else:
        otu_graph = absolute_value_edges(G)

    l_part =[]


    #Create community partition multiple times to obtain a consensus of the partition with highest modularity
    if (seed==None):
        for item in range(0, num_partitions):
            #Obtain consensus partition
            l_part.append(np.asarray(list(community_louvain.best_partition(otu_graph).values())))
        
        consensus = cluster.find_consensus(np.column_stack(l_part))
    else:
        for item in range(0, num_partitions):
            l_part.append(np.asarray(list(community_louvain.best_partition(otu_graph, random_state=item).values())))
    
        consensus = cluster.find_consensus(np.column_stack(l_part), seed=seed)


    nodes_names = list(otu_graph.nodes)
    best_partition = pd.DataFrame({'OTUs': nodes_names, 'consensus_partition': consensus})
    return best_partition