from pandas import read_csv
from networkx import read_graphml
from qiime2.plugin.testing import TestPluginBase

import q2_makarsa._louvain


class TestLouvain(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        network = read_graphml(self.get_data_path("network.graphml"))
        observed = q2_makarsa._louvain.louvain_communities(
            network=network, deterministic=True)
        expected = read_csv(
            self.get_data_path("louvain.tsv"), sep='\t', header=0)
        observed = self.dataframe_to_partition(observed)
        expected = self.dataframe_to_partition(expected)
        print(f"Observed: {observed}")
        print(f"Expected: {expected}")
        self.assertTrue(observed == expected)

    def test_networkx(self):
        network = read_graphml(self.get_data_path("network.graphml"))
        try:
            scikit_network = q2_makarsa._louvain.scikit_network
            q2_makarsa._louvain.scikit_network = False
            observed = q2_makarsa._louvain.louvain_communities(
                network=network, deterministic=True)
        finally:
            q2_makarsa._louvain.scikit_network = scikit_network
        expected = read_csv(
            self.get_data_path("louvain.tsv"), sep='\t', header=0)
        observed = self.dataframe_to_partition(observed)
        expected = self.dataframe_to_partition(expected)
        print(f"Observed: {observed}")
        print(f"Expected: {expected}")
        self.assertTrue(observed == expected)

    def dataframe_to_partition(self, df):
        """
        Convert a DataFrame to a partition dictionary.
        """
        partitions = set()
        for parttions in df['Community'].unique():
            partitions.add(
                frozenset(df[df['Community'] == parttions]['feature id']))
        return partitions

    def test_graph_to_sparse_matrix(self):
        network = read_graphml(self.get_data_path("network.graphml"))
        # print the network as a dictionary
        detector = q2_makarsa._louvain.LouvainCommunityDetector(network)
        sparse_matrix = detector._graph_to_sparse(network)
        round_trip = detector._build_adjacency(sparse_matrix)
        self.assertEqual(len(network.nodes), len(round_trip.nodes))
        self.assertEqual(len(network.edges), len(round_trip.edges))
        for u, v in network.edges:
            self.assertEqual(network[u][v]['weight'], round_trip[u][v]['weight'])
        for u, v in round_trip.edges:
            self.assertEqual(network[u][v]['weight'], round_trip[u][v]['weight'])
        