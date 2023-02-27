import tempfile
from pathlib import Path

from networkx import Graph, read_graphml
import networkx.algorithms.isomorphism as iso
from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase


class TestNetwork(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_network(self):
        network_filename = self.get_data_path("network.graphml")
        before = read_graphml(network_filename)
        before_artifact = Artifact.import_data("Network", before)
        with tempfile.TemporaryDirectory() as temp_dir_name:
            artifact_filename = str(Path(temp_dir_name) / "test.qza")
            before_artifact.save(artifact_filename)
            after_artifact = Artifact.load(artifact_filename)
            after = after_artifact.view(Graph)
        self.assertTrue(iso.is_isomorphic(before, after))
