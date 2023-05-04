import networkx as nx
import pandas as pd
from ._network import NetworkDirectoryFormat


def louvain_communities(
                        network_input: NetworkDirectoryFormat,
                        num_partitions: int = 100,
                        remove_neg: bool = False,
                        deterministic: bool = False,
                        threshold: float = 0.3
                        ) -> pd.DataFrame:
    # load data and create network graph

    G = nx.read_graphml("/".join([str(network_input), "network.graphml"]))

    def remove_negative_edges(G):
        # Remove the negative edges from the graph
        G_new = nx.Graph()
        G_new.add_nodes_from(G.nodes())
        for u, v, weight in G.edges(data='weight'):
            if weight >= 0:
                G_new.add_edge(u, v, weight=weight)
        return G_new

    # Get absolute weights of the graph
    def absolute_value_edges(G):
        for u, v, data in G.edges(data=True):
            data['weight'] = abs(data['weight'])
        return G

    if remove_neg is True:
        G = remove_negative_edges(G)
    else:
        G = absolute_value_edges(G)

    def divide_nonzero(x):
        return x / num_partitions if x != 0 else 0

    def consensus_matrix(G,  # Networkx graph object
                         num_partitions: int = 100,
                         deterministic: bool = False):
        louvain_sum = pd.DataFrame()
        for i in range(num_partitions):
            if deterministic is False:
                best_partition = nx.community.louvain_communities(G)
            else:
                best_partition = nx.community.louvain_communities(G, seed=i)
            louvain_df = list_to_dataframe(best_partition)
            # Add partitons
            louvain_sum = louvain_sum.add(louvain_df, fill_value=0)
        # Divide by the total number of partitions
        louvain_sum = louvain_sum.applymap(divide_nonzero)
        return louvain_sum

    def threshold_filter(c_matrix,  # Consensus matrix obtained with
                         threshold: float = 0.3):
        c_matrix[c_matrix < threshold] = 0
        return c_matrix

    def consensus_to_nodemap(c_matrix):
        # convert matrix to graph
        graph = nx.from_pandas_adjacency(c_matrix)
        # Obtain communities in Networkx format by iterating over the nodes
        communities = []
        visited = set()
        for node in graph.nodes:
            if node not in visited:
                community = set(nx.neighbors(graph, node)) | {node}
                visited |= community
                communities.append(community)
        # Obtain nodemap
        dic = {}
        for num, comm in enumerate(communities):
            for node in comm:
                dic[node] = num
        return dic

    def list_to_dataframe(
                        community_list: list):
        # Obtain a set of the nodes in the list
        nodes_set = set()
        for comm in community_list:
            nodes_set.update(comm)
        # Create dataframe for the partition
        df = pd.DataFrame(columns=list(nodes_set))
        for node in nodes_set:
            for comm in community_list:
                if node in comm:
                    li = [1 if x in comm else 0 for x in nodes_set]
                    df.loc[node] = li
                    break
        return df

    # Flag variable to change when the consenus is reached
    different_consensus = True
    count = 1
    while (different_consensus):
        if count == 1:
            consensus_1 = consensus_matrix(G, num_partitions, deterministic)
            # Check if all the partitions are the same
            if consensus_1.isin([0, 1]).all().all():
                # convert to networkx community format
                final_consensus = consensus_to_nodemap(consensus_1)
                print("Converged at iteration %d \n" % count)
                break
        # Apply threshold to set variables to 0
        consensus_1 = threshold_filter(consensus_1, threshold)
        # Convert to networkx graph
        graph = nx.from_pandas_adjacency(consensus_1)
        consensus_2 = consensus_matrix(graph, num_partitions, deterministic)
        if consensus_2.isin([0, 1]).all().all():
            # convert to networkx community format
            final_consensus = consensus_to_nodemap(consensus_2)
            different_consensus = False
            print("Converged at iteration %d \n" % count)
        else:
            consensus_1 = consensus_2
            count += 1
    # Convert to final format in dictionary keys-nodes values-community
    final_partition = pd.DataFrame({
        'OTUID': list(final_consensus.keys()),
        'COMMUNITY': final_consensus.values()
        })

    return final_partition
