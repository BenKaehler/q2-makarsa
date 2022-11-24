import subprocess
import tempfile
import unittest
from pathlib import Path

import biom
import networkx as nx
from networkx import read_graphml
import pandas as pd
import qiime2
from qiime2 import Artifact
import skbio
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin.testing import TestPluginBase

from pretty_easi._spieceasi import spiec_easi


class Testspieceasioutput(TestPluginBase):
    package = "pretty_easi.tests"

    def setUp(self):
        super().setUp()
        self.empty_table = self.get_data_path("table.biom")
        self.empty_table = Artifact.import_data("FeatureTable[Frequency]", self.empty_table)
        self.df = self.empty_table.view(pd.DataFrame)

        self.network = self.get_data_path("out.graphml")
        

        #self.empty_network = Artifact.import_data("Network", self.empty_network)
        #Artifact.load(self.empty_network)
        #self.expected_network = self.empty_network.view(Network)

    def test_defaults(self):

        generated_network = spiec_easi(self.df, method='mb')  # output from qiime plugin
        expected_network=read_graphml(self.network)
        nx.draw(expected_network)
        print(generated_network.nodes())
        #print(generated_network.degree())
        #print(generated_network.edges())
        
        print(expected_network.nodes())
        #print(expected_network.degree())
        #print(expected_network.edges())
        
        my_list = [(a,b) for (a,b) in expected_network.degree() for (c,d) in generated_network.degree() if ((a==c) and (b==d))]
        for i in generated_network.degree():
            if i in my_list:
                 print("Match node with degree: ", i)
            else:
                 print("Mismatch node with degree : ", i)
        
        
        my_list_edges = [(a,b) for (a,b) in expected_network.edges() for (c,d) in generated_network.edges() if ((a==c) and (b==d))or((a==d) and (b==c))]
        for i in generated_network.edges():
            if i in my_list_edges:
                 print("Match edge : ", i)
            else:
                 print("Mismatch edge : ", i) 
        
       # self.assertEqual(generated_network.nodes(), expected_network.nodes()) 
        #self.assertEqual(generated_network.degree(), expected_network.degree())
        #self.assertEqual(table, exp_table)
       # self.assertEqual(generated_network.edges(), expected_network.edges())

if __name__ == "__main__":
    unittest.main()