from networkx import read_graphml, write_graphml, Graph

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
def _1(network: Graph) -> NetworkFormat:
    ff = NetworkFormat()
    write_graphml(network, str(ff))
    return ff


@plugin.register_transformer
def _2(ff: NetworkFormat) -> Graph:
    return read_graphml(str(ff))


plugin.visualizers.register_function(
    function=visualise_network,
    inputs={'network': Network},
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
        'rep_num': qiime2.plugin.Int,
        'ncores': qiime2.plugin.Int,
        'thresh': qiime2.plugin.Float,
        'subsample.ratio': qiime2.plugin.Float,
        'seed': qiime2.plugin.Float,
        'wkdir': qiime2.plugin.Str,
        'regdir': qiime2.plugin.Str,
        'init': qiime2.plugin.Str,
        'conffile': qiime2.plugin.Str,
        'job.res': qiime2.plugin.Float,
        'cleanup': qiime2.plugin.bool,
        'sel.criterion': qiime2.plugin.Str,
        'verbose': qiime2.plugin.bool,
        'pulsar.select': qiime2.plugin.Str,
        'nlambda.log': qiime2.plugin.bool
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
        
        'rep_num': 'Input parameter of spieceasi ',
        
        'ncores': 'Number of cores for parallel computation',
        
        'thresh': 'Threshold for StARS criterion',
        
        'subsample.ratio': 'Subsample size for StARS',
        
        'seed': 'Set the random seed for subsample set',
        
        'wkdir': 'Current working directory for process running jobs',
        
        'regdir': 'Directory for storing the registry files',
        
        'init': 'String for differentiating the init registry for batch mode pulsar',
        
        'conffile': 'Path to config file or string that identifies a default config file',
        
        'job.res': 'Named list to specify job resources for an hpc',
        
        'cleanup': 'Remove registry files, either TRUE or FALSE',
        
        'sel.criterion': 'Specifying criterion/method for model selection, Accepts 'stars' [default], 'bstars' (Bounded StARS)',
        
        'verbose': 'Print extra output [default]',
        
        'pulsar.select': "Perform model selection. Choices are TRUE/FALSE/'batch' ",
        
        'nlambda.log': 'lambda.log should values of lambda be distributed logarithmically (TRUE) or linearly (FALSE) between lamba.min and lambda.max'     
    },
    output_descriptions={
        'network': 'The inferred network'
    },
    name='SpiecEasi',
    description=('This method generates the sparse matrix of network of input '
                 'data')
)
