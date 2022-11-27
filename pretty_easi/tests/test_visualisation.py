import tempfile
import unittest
import networkx as nx
from networkx import (read_graphml,Graph)
import qiime2
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase
from pretty_easi._visualisation import (graph_to_spec, get_connected_components)

class testnetwork(TestPluginBase):
    package = "pretty_easi.tests"

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory(prefix='q2-pretty_easi-test-temp-')
        self.network = self.get_data_path("network.graphml")
        self.expected_network=read_graphml(self.network)
        self.imported_network = Artifact.import_data("Network", self.expected_network)
        self.qiime_network = self.imported_network.view(Graph)

    def test_defaults(self):
        self.qiime_spec=graph_to_spec(self.qiime_network)
        self.qiime_groups, self.qiime_pairs, self.qiime_singles=get_connected_components(self.qiime_network)
        
        self.expected_spec=graph_to_spec(self.expected_network)
        self.expected_groups, self.expected_pairs, self.expected_singles=get_connected_components(self.expected_network)
        print(self.qiime_groups)
        self.assertEqual(self.expected_spec, self.qiime_spec)
        #self.assertEqual(self.expected_groups, self.qiime_groups)
        self.assertEqual(self.expected_pairs, self.qiime_pairs)
        self.assertEqual(self.expected_singles, self.qiime_singles)
        

if __name__ == "__main__":
    unittest.main()