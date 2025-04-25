import networkx as nx
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import numpy as np
from collections import defaultdict

try:
    from sknetwork.clustering import Louvain
    scikit_network = True
except ImportError:
    scikit_network = False


class LouvainCommunityDetector:
    """
    Perform consensus-based Louvain community detection on a NetworkX graph.
    """

    def __init__(
        self,
        network: nx.Graph,
        num_partitions_consensus: int = 100,
        num_partitions_convergence: int = 100,
        remove_neg: bool = False,
        deterministic: bool = False,
        num_jobs_consensus: int = 1,
        num_jobs_convergence: int = 1,
        max_iter: int = 100,
        threshold: float = 0.3,
    ):
        if not scikit_network:
            print("Warning: scikit-network not installed. "
                  "Falling back to NetworkX for community detection.")

        self.num_partitions_consensus = num_partitions_consensus
        self.num_partitions_convergence = num_partitions_convergence
        self.remove_neg = remove_neg
        self.deterministic = deterministic
        self.num_jobs_consensus = num_jobs_consensus
        self.num_jobs_convergence = num_jobs_convergence
        self.max_iter = max_iter
        self.threshold = threshold

        # Copy and preprocess network
        self.network = nx.Graph(network)
        if self.remove_neg:
            self.network = self._filter_negative(self.network)
        else:
            self.network = self._abs_weight(self.network)

        # Node indexing
        self.nodes = list(self.network.nodes)
        self.node_idx = {node: i for i, node in enumerate(self.nodes)}

        # Choose integer dtype for consensus counts
        max_parts = max(
            self.num_partitions_consensus,
            self.num_partitions_convergence,
        )
        if max_parts <= np.iinfo(np.uint8).max:
            self.dtype = np.uint8
        elif max_parts <= np.iinfo(np.uint16).max:
            self.dtype = np.uint16
        elif max_parts <= np.iinfo(np.uint32).max:
            self.dtype = np.uint32
        else:
            self.dtype = np.uint64

    @staticmethod
    def _filter_negative(G: nx.Graph) -> nx.Graph:
        """
        Remove edges with negative weight.
        """
        filtered = nx.Graph()
        filtered.add_nodes_from(G.nodes(data=True))
        for u, v, w in G.edges(data='weight'):
            if w >= 0:
                filtered.add_edge(u, v, weight=w)
        return filtered

    @staticmethod
    def _abs_weight(G: nx.Graph) -> nx.Graph:
        """
        Convert all edge weights to their absolute values.
        """
        result = nx.Graph()
        result.add_nodes_from(G.nodes(data=True))
        for u, v, data in G.edges(data=True):
            weight = data.get('weight', 1)
            result.add_edge(u, v, weight=abs(weight))
        return result

    def _build_adjacency(self, graph: csr_matrix) -> nx.Graph:
        """
        Convert a sparse matrix back to a NetworkX graph with attrs.
        """
        G = nx.Graph()
        G.add_nodes_from(self.network.nodes(data=True))
        graph.eliminate_zeros()
        rows, cols = graph.nonzero()
        for i, j, w in zip(rows, cols, graph.data):
            G.add_edge(self.nodes[i], self.nodes[j], weight=w)
        return G

    def _graph_to_sparse(self, G: nx.Graph) -> csr_matrix:
        """
        Convert NetworkX graph to sparse adjacency matrix (float64).
        """
        n = len(self.nodes)
        rows, cols, data = [], [], []
        for u, v, d in G.edges(data='weight'):
            rows.append(self.node_idx[u])
            cols.append(self.node_idx[v])
            data.append(d)
        return csr_matrix((data, (rows, cols)), shape=(n, n))

    def partition_to_sparse(self, partition) -> csr_matrix:
        """
        Turn a partition into a half adjacency matrix of co-community counts.
        """
        if isinstance(partition, dict):
            comms = defaultdict(list)
            for node, cid in partition.items():
                comms[cid].append(node)
            groups = comms.values()
        else:
            groups = partition

        rows, cols = [], []
        for group in groups:
            idxs = [self.node_idx[n] for n in group]
            for i in idxs:
                for j in idxs:
                    if j <= i:
                        rows.append(i)
                        cols.append(j)
        # data = [self.dtype(1)] * len(rows)
        data = np.ones(len(rows), dtype=self.dtype)
        n = len(self.nodes)
        return csr_matrix((data, (rows, cols)), shape=(n, n),
                          dtype=self.dtype)

    def _partial_consensus(
        self,
        adj: csr_matrix,
        seeds: list,
    ) -> csr_matrix:
        """
        Run a batch of Louvain partitions on `seeds` and sum their
        co-membership matrices, including NetworkX fallback.
        """
        n = len(self.nodes)
        agg = csr_matrix((n, n), dtype=self.dtype)
        for seed in seeds:
            if scikit_network:
                model = Louvain(
                    shuffle_nodes=True,
                    random_state=seed if self.deterministic else None,
                )
                labels = model.fit_predict(adj)
                partition = {self.nodes[i]: c
                             for i, c in enumerate(labels)}
            else:
                G_nx = self._build_adjacency(adj)
                if self.deterministic:
                    partition = nx.community.louvain_communities(
                        G_nx, seed=seed
                    )
                else:
                    partition = nx.community.louvain_communities(
                        G_nx
                    )
            agg += self.partition_to_sparse(partition)
        return agg

    def consensus_matrix(
        self,
        adj: csr_matrix,
        num_partitions: int,
        deterministic: bool,
        num_jobs: int,
    ) -> csr_matrix:
        seeds = list(range(num_partitions))
        chunks = [seeds[i::num_jobs] for i in range(num_jobs)]

        partials = Parallel(
            n_jobs=num_jobs,
            verbose=10,
        )(delayed(self._partial_consensus)(adj, chunk)
          for chunk in chunks)

        total = sum(
            partials,
            csr_matrix((len(self.nodes), len(self.nodes)),
                       dtype=self.dtype),
        )
        return total

    @staticmethod
    def _converged_count(matrix: csr_matrix, num_partitions: int) -> int:
        """
        Count the number of pairs that always co-occur in the same community.
        """
        data = matrix.data
        return np.sum(data == num_partitions) + matrix.shape[0]**2 - len(data)

    def detect_communities(self) -> pd.DataFrame:
        """
        Main entry: build consensus, threshold, extract communities.
        """
        adj = self._graph_to_sparse(self.network)
        consensus = self.consensus_matrix(
            adj,
            self.num_partitions_consensus,
            self.deterministic,
            self.num_jobs_consensus,
        )

        consensus.eliminate_zeros()
        if np.all(consensus.data == self.num_partitions_consensus):
            print("Converged after initial consensus.")
        else:
            total = consensus.shape[0]**2
            count = self._converged_count(
                consensus, self.num_partitions_consensus
            )
            print(f"Iteration 0: {count}/{total}")
            thresh = self.dtype(
                round(
                    self.threshold
                    * self.num_partitions_convergence,
                )
            )
            for it in range(1, self.max_iter + 1):
                consensus.data[consensus.data < thresh] = 0
                consensus.eliminate_zeros()
                consensus = self.consensus_matrix(
                    consensus,
                    self.num_partitions_convergence,
                    self.deterministic,
                    self.num_jobs_convergence,
                )
                consensus.eliminate_zeros()
                if np.all(
                    consensus.data == self.num_partitions_convergence
                ):
                    print(f"Converged at iteration {it}")
                    break
                count = self._converged_count(
                    consensus, self.num_partitions_convergence
                )
                print(f"Iteration {it}: {count}/{total}")
            else:
                print("Warning: Max iterations reached without convergence.")
                print(f"Final count: {count}/{total}")

        _, labels = connected_components(consensus, directed=False)
        nodemap = {n: labels[i] for i, n in enumerate(self.nodes)}
        return pd.DataFrame({
            'feature id': [
                self.network.nodes[n]['Feature'] for n in self.nodes
            ],
            'Community': [nodemap[n] for n in self.nodes],
        })


def louvain_communities(
    network: nx.Graph,
    num_partitions_consensus: int = 100,
    num_partitions_convergence: int = 100,
    remove_neg: bool = False,
    deterministic: bool = False,
    num_jobs_consensus: int = 1,
    num_jobs_convergence: int = 1,
    max_iter: int = 100,
    threshold: float = 0.3,
) -> pd.DataFrame:
    """
    Detect communities in a network using consensus Louvain.
    """
    detector = LouvainCommunityDetector(
        network,
        num_partitions_consensus,
        num_partitions_convergence,
        remove_neg,
        deterministic,
        num_jobs_consensus,
        num_jobs_convergence,
        max_iter,
        threshold,
    )
    return detector.detect_communities()
