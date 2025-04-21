from pandas import read_csv
from networkx import read_graphml
from qiime2.plugin.testing import TestPluginBase

from q2_makarsa._louvain import louvain_communities


class TestLouvain(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        network = read_graphml(self.get_data_path("network.graphml"))
        observed = louvain_communities(network=network, deterministic=True)
        expected = read_csv(
            self.get_data_path("louvain.tsv"), sep='\t', header=0)
        observed = self.dataframe_to_partition(observed)
        expected = self.dataframe_to_partition(expected)
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
