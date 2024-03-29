from networkx import read_gml
import networkx.algorithms.isomorphism as iso
from qiime2.plugin.testing import TestPluginBase
import biom

from q2_makarsa._flashweave import flashweave


class TestFlashweave(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        table = biom.load_table(self.get_data_path("table.biom"))
        table_T = table.transpose()
        df = table_T.to_dataframe()
        observed = flashweave(df)
        expected = read_gml(self.get_data_path("network-fw.gml"))
        self.assertTrue(iso.is_isomorphic(observed, expected))
