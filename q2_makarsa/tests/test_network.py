import unittest

from networkx import Graph, read_graphml
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase


class testnetwork(TestPluginBase):
    package = "q2_makarsa.tests"

    def setUp(self):
        super().setUp()
        self.network = self.get_data_path("network.graphml")
        self.expected_network = read_graphml(self.network)
        self.imported_network = Artifact.import_data(
            "Network", self.expected_network
        )
        self.qiime_network = self.imported_network.view(Graph)

    def test_defaults(self):
        my_list = [
            (a, b)
            for (a, b) in self.expected_network.degree()
            for (c, d) in self.qiime_network.degree()
            if ((a == c) and (b == d))
        ]
        for i in self.qiime_network.degree():
            if i in my_list:
                self.assertTrue(True)
            else:
                self.assertTrue(False)

        my_list_edges = [
            (a, b)
            for (a, b) in self.expected_network.edges()
            for (c, d) in self.qiime_network.edges()
            if ((a == c) and (b == d)) or ((a == d) and (b == c))
        ]
        for i in self.qiime_network.edges():
            if i in my_list_edges:
                self.assertTrue(True)
            else:
                self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
