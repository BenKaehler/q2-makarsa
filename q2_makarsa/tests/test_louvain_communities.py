from pandas import read_csv
from qiime2.plugin.testing import TestPluginBase

from q2_makarsa._louvain.py import louvain_communities


class TestLouvain(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        network = self.get_data_path("network.graphml")
        observed = louvain_communities(network_input=network,
                                       deterministic=True)
        expected = read_csv(self.get_data_path("pd.DataFrame"),
                            sep='\t', header=0)
        self.assertTrue(observed.equals(expected))
