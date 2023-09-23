from networkx import read_graphml
import networkx.algorithms.isomorphism as iso
from qiime2.plugin.testing import TestPluginBase
import biom
import qiime2 as q2
import pandas as pd

from q2_makarsa._spieceasi import spiec_easi, encode_metadata


class TestSpieceasi(TestPluginBase):
    package = "q2_makarsa.tests"

    def test_defaults(self):
        table = biom.load_table(self.get_data_path("table.biom"))
        observed = spiec_easi([table], rep_num=5)
        expected = read_graphml(self.get_data_path("network.graphml"))
        self.assertTrue(iso.is_isomorphic(observed, expected))

    def test_cross_domain(self):
        hmp216S = biom.load_table(self.get_data_path("hmp216S.biom"))
        hmp2prot = biom.load_table(self.get_data_path("hmp2prot.biom"))
        observed = spiec_easi([hmp216S, hmp2prot], rep_num=5)
        expected = read_graphml(self.get_data_path("network-cd.graphml"))
        self.assertTrue(iso.is_isomorphic(observed, expected))

    def test_encode_metadata(self):
        sample_ids = list("ABCD")
        df = pd.DataFrame(
            {"foo": ["a", "b", "c", "a"], "bar": [1, 2, 3, 4]},
            index=sample_ids)
        df.index.name = "feature id"

        metadata = q2.Metadata(df)
        observed = encode_metadata(sample_ids, metadata)
        observed = [t.to_dataframe().sparse.to_dense() for t in observed]

        expected = [
            {
                'A': {'foo a': 7.3421447164767955, 'foo b': 0.0, 'foo c': 0.0},
                'B': {'foo a': 0.0, 'foo b': 7.3421447164767955, 'foo c': 0.0},
                'C': {'foo a': 0.0, 'foo b': 0.0, 'foo c': 7.3421447164767955},
                'D': {'foo a': 7.3421447164767955, 'foo b': 0.0, 'foo c': 0.0}
            },
            {
                'A': {'bar High': 0.0, 'bar Low': 6.38905609893065},
                'B': {'bar High': 0.0, 'bar Low': 6.38905609893065},
                'C': {'bar High': 6.38905609893065, 'bar Low': 0.0},
                'D': {'bar High': 6.38905609893065, 'bar Low': 0.0}
            }
        ]
        expected = [pd.DataFrame(t) for t in expected]

        for o, e in zip(observed, expected):
            pd.testing.assert_frame_equal(o, e)
