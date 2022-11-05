from scipy.io import mmread, mmwrite
from scipy.sparse import coo_matrix

import qiime2
from qiime2.plugin import Plugin
from q2_types.feature_table import FeatureTable, Frequency

from ._visualisation import visualise_network
from ._spieceasi import spiec_easi
from ._network import Network, NetworkDirectoryFormat, NetworkFormat


plugin = Plugin(
    name='spieceasi',
    version='0.0.0-dev',
    website='https://github.com/BenKaehler/q2-SpiecEasi/tree/main/q2_SpiecEasi',  # noqa
    package='q2_SpiecEasi',
    description=('This QIIME 2 plugin wraps SpiecEasi '
                 'and will be useful to anybody who wants to infer '
                 'graphical models for all sorts of compositional '
                 'data, though primarily intended for microbiome '
                 'relative abundance data (generated from 16S '
                 'amplicon sequence data).'),
    short_description='A QIIME 2 plugin to expose some SpiecEasi '
                      'functionality.',
    # citations=qiime2.plugin.Citations.load(
    #    'citations.bib', package='q2_dada2'
)

plugin.register_semantic_types(Network)
plugin.register_formats(NetworkDirectoryFormat, NetworkFormat)
plugin.register_semantic_type_to_format(
        Network, artifact_format=NetworkDirectoryFormat)


@plugin.register_transformer
def _1(matrix: coo_matrix) -> (NetworkFormat):
    ff = NetworkFormat()
    with open(str(ff), 'wb') as fh:  # raises an error without the ugly 'wb'
        mmwrite(fh, matrix)
    return ff


@plugin.register_transformer
def _2(ff: NetworkFormat) -> coo_matrix:
    with open(str(ff)) as fh:
        return mmread(fh)


plugin.visualizers.register_function(
    function=visualise_network,
    inputs={},
    parameters={},
    name='Visualize network',
    description='Create an interactive depiction of your network.'
)


plugin.methods.register_function(
    function=spiec_easi,
    inputs={'table': FeatureTable[Frequency]},
    parameters={
        'method': qiime2.plugin.Str,
        'lambda_min_ratio': qiime2.plugin.Float,
        'nlambda': qiime2.plugin.Int,
        'rep_num': qiime2.plugin.Int
    },
    outputs=[('network', Network)],
    input_descriptions={
        'table': ('All sorts of compositional data though primarily intended '
                  'for microbiome relative abundance data '
                  '(generated from 16S amplicon sequence data)')
    },
    parameter_descriptions={
        'method': 'Methods available for spieceasi,for example mb,glasso,slr',
        'lambda_min_ratio': ('Input parameter of spieceasi which represents '
                             'the scaling factor that determines the minimum '
                             'sparsity/lambda parameter'),
        'nlambda': 'Input parameter of spieceasi ',
        'rep_num': 'Input parameter of spieceasi '
    },
    output_descriptions={
        'network': 'The inferred network'
    },
    name='SpiecEasi',
    description=('This method generates the sparse matrix of network of input '
                 'data')
)
