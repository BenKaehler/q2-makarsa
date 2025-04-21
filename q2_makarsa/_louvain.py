import networkx as nx
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix, lil_matrix
import numpy as np
from scipy.sparse.csgraph import connected_components


def louvain_communities(
                        network: nx.Graph,
                        num_partitions: int = 100,
                        remove_neg: bool = False,
                        deterministic: bool = False,
                        num_jobs: int = 1,
                        max_iter: int = 100,
                        threshold: float = 0.3
                        ) -> pd.DataFrame:
    """
    Perform Louvain community detection on a networkx graph.
    Parameters
    ----------
    network : nx.Graph
        The input graph.
    num_partitions : int, optional
        The number of partitions to create. Default is 100.
    remove_neg : bool, optional
        If True, remove negative edges from the graph. Default is False.
    deterministic : bool, optional
        If True, use a deterministic seed for the random number generator.
        Default is False.
    num_jobs : int, optional
        The number of parallel jobs to run. Default is 1.
    max_iter : int, optional
        The maximum number of iterations to run. Default is 100.
    threshold : float, optional
        The threshold for filtering the consensus matrix. Default is 0.3.
    Returns
    -------
    pd.DataFrame
        A DataFrame containing the feature IDs and their corresponding
        community assignments.
    """
    def remove_negative_edges(G):
        G_new = nx.Graph()
        G_new.add_nodes_from(G.nodes())
        for u, v, weight in G.edges(data='weight'):
            if weight >= 0:
                G_new.add_edge(u, v, weight=weight)
        return G_new

    def absolute_value_edges(G):
        for _, __, data in G.edges(data=True):
            data['weight'] = abs(data['weight'])
        return G

    if remove_neg:
        network = remove_negative_edges(network)
    else:
        network = absolute_value_edges(network)

    nodes = list(network.nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    def consensus_matrix(network, num_partitions=100, deterministic=False):
        n = len(nodes)
        louvain_sum = lil_matrix((n, n), dtype=np.float64)

        def process_partition(i):
            if deterministic:
                partition = nx.community.louvain_communities(
                    network, seed=i)
            else:
                partition = nx.community.louvain_communities(network)
            return list_to_sparse_matrix(partition)

        # Run partitions in parallel
        louvain_matrices = Parallel(n_jobs=num_jobs)(
            delayed(process_partition)(i) for i in range(num_partitions)
        )

        # Sum up the partitions
        for louvain_matrix in louvain_matrices:
            louvain_sum += louvain_matrix

        # Divide by the total number of partitions
        louvain_sum = louvain_sum.multiply(1 / num_partitions)
        return csr_matrix(louvain_sum)

    def threshold_filter(c_matrix, threshold=0.3):
        thresholded = c_matrix.multiply(c_matrix >= threshold)
        thresholded.eliminate_zeros()
        return thresholded

    def consensus_to_nodemap(c_matrix):
        _, labels = connected_components(
            c_matrix, connection='strong')
        return {nodes[idx]: label for idx, label in enumerate(labels)}

    def list_to_sparse_matrix(community_list):
        n = len(nodes)
        sparse_matrix = lil_matrix((n, n), dtype=np.float64)
        for community in community_list:
            indices = [node_idx[node] for node in community]
            for i in indices:
                for j in indices:
                    sparse_matrix[i, j] = 1
        return sparse_matrix
    
    def sparse_matrix_to_graph(sparse_matrix):
        graph = nx.Graph()
        sparse_matrix.eliminate_zeros()
        rows, cols = sparse_matrix.nonzero()
        for row, col in zip(rows, cols):
            graph.add_edge(
                nodes[row], nodes[col], weight=sparse_matrix[row, col])
        return graph

    different_consensus = True
    count = 1
    while different_consensus:
        if count == 1:
            consensus_1 = consensus_matrix(
                network, num_partitions, deterministic)
            consensus_1.eliminate_zeros()
            if (consensus_1 == 1).sum() == consensus_1.nnz:
                final_consensus = consensus_to_nodemap(consensus_1)
                break
        consensus_1 = threshold_filter(consensus_1, threshold)
        graph = sparse_matrix_to_graph(consensus_1)
        consensus_2 = consensus_matrix(graph, num_partitions, deterministic)
        consensus_2.eliminate_zeros()
        if (consensus_2 == 1).sum() == consensus_2.nnz or count == max_iter:
            if count == max_iter:
                print("Max iterations reached")
            else:
                print(f"Converged at iteration {count}")
            final_consensus = consensus_to_nodemap(consensus_2)
            different_consensus = False
        else:
            consensus_1 = consensus_2
            count += 1
            print(f"Iteration {count}:")
            total_elements = consensus_2.shape[0] * consensus_2.shape[1]
            ok_elements = (consensus_2 == 1).sum() + \
                total_elements - consensus_2.nnz
            print(f"{ok_elements} true out of {total_elements}")

    final_partition = pd.DataFrame({
        'feature id': [network.nodes[k]['Feature'] for k in final_consensus],
        'Community': final_consensus.values()
    })

    return final_partition
