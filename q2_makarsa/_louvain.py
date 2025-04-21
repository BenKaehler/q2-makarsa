import networkx as nx
from community import community_louvain
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix, lil_matrix
import numpy as np
from scipy.sparse.csgraph import connected_components
from collections import defaultdict


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

        def process_partition(i):
            if deterministic:
                partition = community_louvain.best_partition(
                    network, random_state=i)
            else:
                partition = community_louvain.best_partition(network)
            return partition_to_sparse_matrix(partition)

        # Run partitions in parallel
        louvain_matrices = Parallel(n_jobs=num_jobs)(
            delayed(process_partition)(i) for i in range(num_partitions)
        )

        louvain_sum = csr_matrix((n, n), dtype=np.float64)
        for louvain_matrix in louvain_matrices:
            louvain_sum = louvain_sum + louvain_matrix  # Use csr_matrix for efficient addition

        # Divide by the total number of partitions
        louvain_sum = louvain_sum.multiply(1 / num_partitions)
        return csr_matrix(louvain_sum)

    def threshold_filter(c_matrix, threshold=0.3):
        # Retain only elements above the threshold
        c_matrix.data[c_matrix.data < threshold] = 0
        c_matrix.eliminate_zeros()
        return c_matrix

    def consensus_to_nodemap(c_matrix):
        _, labels = connected_components(
            c_matrix, connection='strong')
        return {nodes[idx]: label for idx, label in enumerate(labels)}

    def partition_to_sparse_matrix(partition):
        n = len(nodes)
        sparse_matrix = lil_matrix((n, n), dtype=np.float64)

        # Group nodes by community
        communities = defaultdict(list)
        for node, community in partition.items():
            communities[community].append(node)

        # Fill the sparse matrix
        for community_nodes in communities.values():
            indices = [node_idx[node] for node in community_nodes]
            for i in indices:
                sparse_matrix[i, indices] = 1  # Vectorized assignment
        return sparse_matrix
    
    def sparse_matrix_to_graph(sparse_matrix):
        graph = nx.Graph()
        sparse_matrix.eliminate_zeros()
        rows, cols = sparse_matrix.nonzero()
        for row, col, weight in zip(rows, cols, sparse_matrix.data):
            if weight > 0:  # Only add edges with positive weights
                graph.add_edge(nodes[row], nodes[col], weight=weight)
        return graph

    different_consensus = True
    count = 1
    while different_consensus:
        if count == 1:
            consensus_1 = consensus_matrix(
                network, num_partitions, deterministic)
            consensus_1.eliminate_zeros()
            if np.all(consensus_1.data == 1):
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
