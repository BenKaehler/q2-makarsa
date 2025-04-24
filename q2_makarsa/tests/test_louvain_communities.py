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
            python_louvain = q2_makarsa._louvain.python_louvain
            q2_makarsa._louvain.python_louvain = False
            observed = q2_makarsa._louvain.louvain_communities(
                network=network, deterministic=True)
        finally:
            q2_makarsa._louvain.python_louvain = python_louvain
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
