from pandas import read_csv
from qiime2.plugin.testing import TestPluginBase

from q2_makarsa._louvain import louvain_communities


class TestLouvain(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        network = self.get_data_path("")
        observed = louvain_communities(network_input=network,
                                       deterministic=True)
        observed = observed.sort_values(by='OTUID').reset_index(drop=True)
        expected = read_csv(self.get_data_path("louvain.tsv"),
                            sep='\t', header=0)
        self.assertTrue(observed.equals(expected))
