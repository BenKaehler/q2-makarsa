import subprocess
import tempfile
import unittest
from pathlib import Path

import biom
import networkx as nx
import pandas as pd
import qiime2
import skbio
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin.testing import TestPluginBase

from q2_SpiecEasi._spieceasi import spiec_easi


class Testspieceasioutput(TestPluginBase):
    package = "q2_SpiecEasi.tests"

    def setUp(self):
        super().setUp()
        empty_table = self.get_data_path("table.tsv")
        self.empty_table = Artifact.import_data("FeatureTable[Frequency]", empty_table)
        df = self.empty_table.view(pd.DataFrame)

        empty_network = self.get_data_path("network.graphml ")

        self.empty_network = Artifact.import_data("Network", empty_network)
        expected_network = self.empty_network.view(nx.Graph())

    def test_defaults(self):

        generated_network = spieceasi(self.df)  # output from qiime plugin

    # self.assertEqual(table, exp_table) # assert


if __name__ == "__main__":
    unittest.main()
