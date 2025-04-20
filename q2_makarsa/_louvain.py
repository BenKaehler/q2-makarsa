import networkx as nx
import pandas as pd
from joblib import Parallel, delayed


def louvain_communities(
                        network: nx.Graph,
                        num_partitions: int = 100,
                        remove_neg: bool = False,
                        deterministic: bool = False,
                        num_jobs: int = 1,
                        max_iter: int = 100,
                        threshold: float = 0.3
                        ) -> pd.DataFrame:
    # load data and create network graph

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
        network = remove_negative_edges(network)
    else:
        network = absolute_value_edges(network)

    def divide_nonzero(x):
        return x / num_partitions if x != 0 else 0

    def consensus_matrix(network,  # Networkx graph object
                         num_partitions: int = 100,
                         deterministic: bool = False):
        louvain_sum = pd.DataFrame()

        def process_partition(i):
            if deterministic is False:
                best_partition = nx.community.louvain_communities(network)
            else:
                best_partition = nx.community.louvain_communities(
                    network, seed=i)
            return list_to_dataframe(best_partition)

        # Run partitions in parallel
        louvain_dfs = Parallel(n_jobs=num_jobs)(
            delayed(process_partition)(i) for i in range(num_partitions)
        )

        # Sum up the partitions
        for louvain_df in louvain_dfs:
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
            consensus_1 = consensus_matrix(
                    network, num_partitions, deterministic)
            # Check if all the partitions are the same
            if consensus_1.isin([0, 1]).all().all():
                # convert to networkx community format
                final_consensus = consensus_to_nodemap(consensus_1)
                print(f"Converged at iteration {count}")
                break
        # Apply threshold to set variables to 0
        consensus_1 = threshold_filter(consensus_1, threshold)
        # Convert to networkx graph
        graph = nx.from_pandas_adjacency(consensus_1)
        consensus_2 = consensus_matrix(graph, num_partitions, deterministic)
        if consensus_2.isin([0, 1]).all().all() or count == max_iter:
            if count == max_iter:
                print("Max iterations reached")
            else:
                print(f"Converged at iteration {count}")
            # convert to networkx community format
            final_consensus = consensus_to_nodemap(consensus_2)
            different_consensus = False
        else:
            consensus_1 = consensus_2
            count += 1
            print(f"Iteration {count}:")
            print(f"{consensus_2.isin([0, 1]).sum().sum()} "
                  f"true out of {consensus_2.size}")

    # Convert to final format in dictionary keys-nodes values-community
    final_partition = pd.DataFrame({
        'feature id': [network.nodes[k]['Feature'] for k in final_consensus],
        'Community': final_consensus.values()
        })

    return final_partition
