from pandas import read_csv
from networkx import read_graphml
from qiime2.plugin.testing import TestPluginBase

from q2_makarsa._louvain import louvain_communities


class TestLouvain(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        network = read_graphml(self.get_data_path("network.graphml"))
        observed = louvain_communities(network=network, deterministic=True)
        observed = observed.sort_values(by='feature id').reset_index(drop=True)
        expected = read_csv(
            self.get_data_path("louvain.tsv"), sep='\t', header=0)
        self.assertTrue(observed.equals(expected))
