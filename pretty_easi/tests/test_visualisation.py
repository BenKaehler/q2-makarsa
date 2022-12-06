import tempfile
import unittest
<<<<<<< HEAD
import networkx as nx
from networkx import (read_graphml,Graph)
import qiime2
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase
from pretty_easi._visualisation import (graph_to_spec, get_connected_components)
=======

from networkx import Graph, read_graphml
from pretty_easi._visualisation import get_connected_components, graph_to_spec
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase
>>>>>>> a83a19559b1a3983404988eae9ac521bf1a54aec


class testnetwork(TestPluginBase):
    package = "pretty_easi.tests"

    def setUp(self):
        super().setUp()
<<<<<<< HEAD
        self.temp_dir = tempfile.TemporaryDirectory(prefix='q2-pretty_easi-test-temp-')
        self.network = self.get_data_path("network.graphml")
        self.expected_network=read_graphml(self.network)
        self.imported_network = Artifact.import_data("Network", self.expected_network)
        self.qiime_network = self.imported_network.view(Graph)

    def test_graph_to_spec(self):
        self.qiime_spec=graph_to_spec(self.qiime_network)        
        self.expected_spec=graph_to_spec(self.expected_network)
        
        self.assertEqual(self.expected_spec, self.qiime_spec)
        
    def test_get_connected_components(self):
        self.qiime_groups, self.qiime_pairs, self.qiime_singles=get_connected_components(self.qiime_network)        
        self.expected_groups, self.expected_pairs, self.expected_singles=get_connected_components(self.expected_network)
           
        if (self.expected_groups==self.qiime_groups):
            self.assertTrue(True)

        self.assertEqual(self.expected_pairs, self.qiime_pairs)
        self.assertEqual(self.expected_singles, self.qiime_singles)    

if __name__ == "__main__":
    unittest.main()
=======
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix="q2-pretty_easi-test-temp-")
        self.network = self.get_data_path("network.graphml")
        self.expected_network = read_graphml(self.network)
        self.imported_network = Artifact.import_data(
            "Network", self.expected_network)
        self.qiime_network = self.imported_network.view(Graph)

    def test_graph_to_spec(self):
        self.qiime_spec = graph_to_spec(self.qiime_network)
        self.expected_spec = graph_to_spec(self.expected_network)

        self.assertEqual(self.expected_spec, self.qiime_spec)

    def test_get_connected_components(self):
        (
            self.qiime_groups,
            self.qiime_pairs,
            self.qiime_singles,
        ) = get_connected_components(self.qiime_network)
        (
            self.expected_groups,
            self.expected_pairs,
            self.expected_singles,
        ) = get_connected_components(self.expected_network)

        if self.expected_groups == self.qiime_groups:
            self.assertTrue(True)

        self.assertEqual(self.expected_pairs, self.qiime_pairs)
        self.assertEqual(self.expected_singles, self.qiime_singles)


if __name__ == "__main__":
    unittest.main()
>>>>>>> a83a19559b1a3983404988eae9ac521bf1a54aec
