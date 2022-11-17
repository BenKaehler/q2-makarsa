
import unittest

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_table import FeatureTable, Frequency
from ._network import Network, NetworkDirectoryFormat, NetworkFormat

import tempfile
import subprocess
from pathlib import Path


import pandas as pd
import networkx as nx


class testnetwork(TestPluginBase):
    package = 'q2_SpiecEasi.tests'

    def setUp(self):
        super().setUp()
        network = self.get_data_path('network.graphml ')
        self.network = Artifact.import_data('Network', network)
        expected_network = self.network.view(nx.Graph())
       
    def test_defaults(self):
        
        

       


if __name__ == '__main__':
    unittest.main()





