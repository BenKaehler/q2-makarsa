import json

from networkx import read_graphml
from qiime2.plugin.testing import TestPluginBase
import qiime2 as q2
import pandas as pd

from q2_makarsa._neighbours import list_neighbours


class TestNeighbours(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_list_neighbours(self):
        expected = pd.read_csv(
            self.get_data_path("neighbours.tsv"),
            sep='\t', header=0, index_col=0)
        network = read_graphml(self.get_data_path("network.graphml"))
        metadata = pd.read_csv(
            self.get_data_path("louvain.tsv"),
            sep='\t', header=0, index_col=0)
        metadata.index.name = "feature id"
        metadata = q2.Metadata(metadata)
        observed = list_neighbours(network, "PfvSC", metadata).to_dataframe()
        pd.testing.assert_frame_equal(observed, expected)
