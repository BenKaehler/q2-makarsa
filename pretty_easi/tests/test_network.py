import subprocess
import tempfile
import unittest
from pathlib import Path

import networkx as nx
import pandas as pd
import qiime2
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin.testing import TestPluginBase

from pretty_easi._network import (Network, NetworkDirectoryFormat,
                                   NetworkFormat)


class testnetwork(TestPluginBase):
    package = "q2_SpiecEasi.tests"

    def setUp(self):
        super().setUp()
        network = self.get_data_path("network.graphml ")
        self.network = Artifact.import_data("Network", network)
        expected_network = self.network.view(nx.Graph())

    def test_defaults(self):

        a = 6
        b = 8
        c = a + b
        # self.assertEqual(table, exp_table) # assert


if __name__ == "__main__":
    unittest.main()
