import unittest

import skbio
import biom
import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_table import FeatureTable, Frequency
from q2_SpiecEasi import spieceasi

import tempfile
import subprocess
from pathlib import Path

from scipy.io import mmread
from scipy.sparse import coo_matrix

import pandas as pd




class Testspieceasioutput(TestPluginBase):
    package = 'q2_SpiecEasi.tests'

    def setUp(self):
        super().setUp()
        self.input_data = SingleLanePerSampleSingleEndFastqDirFmt(  #collecting input data
            self.get_data_path('sample_seqs_single'), 'r')

    def test_defaults(self):
        with open(self.get_data_path('expected/single-default.tsv')) as fh:
           # exp_table = biom.Table.from_tsv(fh, None, None, lambda x: x)
        exp_output = list(
            skbio.io.read(self.get_data_path('expected/single-default.fasta'),
                          'fasta', constructor=skbio.DNA))     # collecting expected output from SpiecEasi
        
        table= spieceasi( self.input_data)   # output from qiime plugin

        self.assertEqual(table, exp_table) # assert
       


if __name__ == '__main__':
    unittest.main()

