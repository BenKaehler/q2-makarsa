import unittest

import pandas as pd
from networkx import read_graphml
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase

from q2_makarsa._spieceasi import spiec_easi


class Testspieceasioutput(TestPluginBase):
    package = "q2_makarsa.tests"

    def setUp(self):
        super().setUp()
        self.empty_table = self.get_data_path("test2.biom")
        self.empty_table = Artifact.import_data(
            "FeatureTable[Frequency]", self.empty_table
        )
        self.df = self.empty_table.view(pd.DataFrame)
        self.network = self.get_data_path("out1.graphml")
        self.generated_network = spiec_easi(
            self.df,
            method="mb",
            lambda_min_ratio=1e-2,
            nlambda=20,
            rep_num=50,
            ncores=16,
        )
        self.expected_network = read_graphml(self.network)
        # nx.draw(expected_network)

    def test_defaults(self):
        my_list = [
            (a, b)
            for (a, b) in self.expected_network.degree()
            for (c, d) in self.generated_network.degree()
            if ((a == c) and (b == d))
        ]

        for i in self.generated_network.degree():
            if i in my_list:
                self.assertTrue(True)
            else:
                self.assertTrue(False)

        my_list_edges = [
            (a, b)
            for (a, b) in self.expected_network.edges()
            for (c, d) in self.generated_network.edges()
            if ((a == c) and (b == d)) or ((a == d) and (b == c))
        ]

        for i in self.generated_network.edges():
            if i in my_list_edges:
                self.assertTrue(True)
            else:
                self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
