import unittest
<<<<<<< HEAD
import networkx as nx
from networkx import (read_graphml,Graph)
import pandas as pd
import qiime2
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase
from pretty_easi._network import (Network, NetworkDirectoryFormat, NetworkFormat)
=======

from networkx import Graph, read_graphml
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase
>>>>>>> a83a19559b1a3983404988eae9ac521bf1a54aec


class testnetwork(TestPluginBase):
    package = "pretty_easi.tests"

    def setUp(self):
        super().setUp()
        self.network = self.get_data_path("network.graphml")
<<<<<<< HEAD
        self.expected_network=read_graphml(self.network)
        self.imported_network = Artifact.import_data("Network", self.expected_network)
        self.qiime_network = self.imported_network.view(Graph)
        

    def test_defaults(self):
        my_list = [(a,b) for (a,b) in self.expected_network.degree() for (c,d) in self.qiime_network.degree() if ((a==c) and (b==d))]
=======
        self.expected_network = read_graphml(self.network)
        self.imported_network = Artifact.import_data(
            "Network", self.expected_network)
        self.qiime_network = self.imported_network.view(Graph)

    def test_defaults(self):
        my_list = [
            (a, b)
            for (a, b) in self.expected_network.degree()
            for (c, d) in self.qiime_network.degree()
            if ((a == c) and (b == d))
        ]
>>>>>>> a83a19559b1a3983404988eae9ac521bf1a54aec
        for i in self.qiime_network.degree():
            if i in my_list:
                self.assertTrue(True)
            else:
                self.assertTrue(False)
<<<<<<< HEAD
        
        
        my_list_edges = [(a,b) for (a,b) in self.expected_network.edges() for (c,d) in self.qiime_network.edges() if ((a==c) and (b==d))or((a==d) and (b==c))]
=======

        my_list_edges = [
            (a, b)
            for (a, b) in self.expected_network.edges()
            for (c, d) in self.qiime_network.edges()
            if ((a == c) and (b == d)) or ((a == d) and (b == c))
        ]
>>>>>>> a83a19559b1a3983404988eae9ac521bf1a54aec
        for i in self.qiime_network.edges():
            if i in my_list_edges:
                self.assertTrue(True)
            else:
                self.assertTrue(False)
<<<<<<< HEAD
=======

>>>>>>> a83a19559b1a3983404988eae9ac521bf1a54aec

if __name__ == "__main__":
    unittest.main()