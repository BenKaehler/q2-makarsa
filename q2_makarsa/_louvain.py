import networkx as nx
try:
    from community import community_louvain
    python_louvain = True
except ImportError:
    python_louvain = False
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
import numpy as np
from scipy.sparse.csgraph import connected_components
from collections import defaultdict


def louvain_communities(
                        network: nx.Graph,
                        num_partitions_consensus: int = 100,
                        num_partitions_convergence: int = 100,
                        remove_neg: bool = False,
                        deterministic: bool = False,
                        num_jobs_consensus: int = 1,
                        num_jobs_convergence: int = 1,
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
    if not python_louvain:
        print("Warning: python-louvain not found. Falling back to networkx.")
        print("This may be slower and less efficient.")

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

    # Use small unsigned ints to reduce memory usage
    max_num_partitions = max(
        num_partitions_consensus, num_partitions_convergence)
    if max_num_partitions <= 255:
        dtype = np.uint8
    elif max_num_partitions <= 65535:
        dtype = np.uint16
    elif max_num_partitions <= 4294967295:
        dtype = np.uint32
    else:
        dtype = np.uint64

    def consensus_matrix(
            graph, num_partitions=100, deterministic=False, num_jobs=1):
        n = len(nodes)

        def process_partition(i):
            try:
                if python_louvain:
                    if deterministic:
                        partition = community_louvain.best_partition(
                            graph, random_state=i)
                    else:
                        partition = community_louvain.best_partition(graph)
                else:
                    # Fallback to networkx
                    if deterministic:
                        partition = nx.community.louvain_communities(
                            graph, seed=i)
                    else:
                        partition = nx.community.louvain_communities(graph)
            except Exception as e:
                print(f"Error in partition {i}: {e}")
                raise
            return partition_to_sparse_matrix(partition)

        # Run partitions in parallel
        louvain_matrices = Parallel(n_jobs=num_jobs, verbose=10)(
            delayed(process_partition)(i) for i in range(num_partitions)
        )

        louvain_sum = csr_matrix((n, n), dtype=dtype)
        for louvain_matrix in louvain_matrices:
            louvain_sum = louvain_sum + louvain_matrix

        return louvain_sum

        # Divide by the total number of partitions
        # return louvain_sum.multiply(1 / num_partitions)

    def threshold_filter(c_matrix, threshold=threshold):
        # Retain only elements above the threshold
        c_matrix.data[c_matrix.data < threshold] = 0
        c_matrix.eliminate_zeros()
        return c_matrix

    def consensus_to_nodemap(c_matrix):
        _, labels = connected_components(c_matrix, directed=False)
        return {nodes[idx]: label for idx, label in enumerate(labels)}

    def partition_to_sparse_matrix(partition):
        # Group nodes by community
        if isinstance(partition, dict):
            communities = defaultdict(list)
            for node, community in partition.items():
                communities[community].append(node)
            communities = communities.values()
        else:
            communities = partition

        # Prepare data for csr_matrix
        row_indices = []
        col_indices = []
        for community_nodes in communities:
            indices = [node_idx[node] for node in community_nodes]
            for i in indices:
                lower_indices = [j for j in indices if j <= i]
                row_indices.extend([i] * len(lower_indices))  # Add row indices
                col_indices.extend(lower_indices)  # Add column indices
        data = [dtype(1)] * len(row_indices)  # All weights are 1

        # Create a csr_matrix directly
        n = len(nodes)
        sparse_matrix = csr_matrix(
            (data, (row_indices, col_indices)), shape=(n, n), dtype=dtype)
        return sparse_matrix

    def sparse_matrix_to_graph(sparse_matrix):
        graph = nx.Graph()
        sparse_matrix.eliminate_zeros()
        rows, cols = sparse_matrix.nonzero()
        for row, col, weight in zip(rows, cols, sparse_matrix.data):
            if weight > 0:
                graph.add_edge(nodes[row], nodes[col], weight=weight)
        return graph

    def print_progress(count, consensus, num_partitions):
        total_elements = consensus.shape[0] * consensus.shape[1]
        ok_elements = (consensus == num_partitions).sum() + \
            total_elements - consensus.nnz
        print(f"Iteration {count}:")
        print(f"{ok_elements} converged out of {total_elements}")

    # Perform inital consensus community detection on input graph
    consensus = consensus_matrix(
        network, num_partitions_consensus, deterministic, num_jobs_consensus)
    consensus.eliminate_zeros()
    if np.all(consensus.data == num_partitions_consensus):
        print("Converged after initial consensus.")
        final_consensus = consensus_to_nodemap(consensus)
    else:
        print_progress(0, consensus, num_partitions_consensus)
        threshold = dtype(np.round(threshold * num_partitions_convergence))
        # Iterate over the consensus matrix to find the final partition
        for count in range(1, max_iter+1):
            consensus = threshold_filter(consensus, threshold)
            graph = sparse_matrix_to_graph(consensus)
            consensus = consensus_matrix(
                graph, num_partitions_convergence,
                deterministic, num_jobs_convergence)
            consensus.eliminate_zeros()
            if np.all(consensus.data == num_partitions_convergence):
                print(f"Converged at iteration {count}")
                final_consensus = consensus_to_nodemap(consensus)
                break
            print_progress(count, consensus)
        else:
            print("Max iterations reached without convergence.")
            final_consensus = consensus_to_nodemap(consensus)

    final_partition = pd.DataFrame({
        'feature id': [network.nodes[k]['Feature'] for k in final_consensus],
        'Community': final_consensus.values()
    })

    return final_partition
