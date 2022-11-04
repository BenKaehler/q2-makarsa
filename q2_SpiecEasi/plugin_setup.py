import qiime2
from qiime2.plugin import Plugin
from q2_types.feature_table import FeatureTable, Frequency

from ._visualisation import visualise_network
from ._spieceasi import SpiecEasi
from ._network import Network


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

plugin.visualizers.register_function(
    function=visualise_network,
    inputs={},
    parameters={},
    name='Visualize network',
    description='Create an interactive depiction of your network.'
)


plugin.methods.register_function(
    function=SpiecEasi,
    inputs={'table', FeatureTable[Frequency]},
    parameters={
        '--method': qiime2.plugin.str,
        '--lambda.min.ratio': qiime2.plugin.Float,
        '--nlambda': qiime2.plugin.Int,
        '--rep.num': qiime2.plugin.Int
    },
    outputs=[('matrix', Network)],
    input_descriptions={
        'table': ('All sorts of compositional data though primarily intended '
                  'for microbiome relative abundance data '
                  '(generated from 16S amplicon sequence data)')
    },
    parameter_descriptions={
        'method': 'Methods available for spieceasi,for example mb,glasso,slr',
        'lambda.min.ratio': ('Input parameter of spieceasi which represents '
                             'the scaling factor that determines the minimum '
                             'sparsity/lambda parameter'),
        'nlambda': 'Input parameter of spieceasi ',
        'rep.num': 'Input parameter of spieceasi '
    },
    output_descriptions={
        'table': 'The resulting feature table.',
        'representative_sequences': ('The resulting feature sequences. Each '
                                     'feature in the feature table will be '
                                     'represented by exactly one sequence.')
    },
    name='SpiecEasi',
    description=('This method generates the sparse matrix of network of input '
                 'data')
)
