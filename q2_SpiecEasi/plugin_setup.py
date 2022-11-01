import importlib

import qiime2.plugin
from q2_types.per_sample_sequences import (
    SequencesWithQuality, PairedEndSequencesWithQuality)
from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData, Sequence
from q2_types.feature_table import FeatureTable, Frequency

import q2_SpiecEasi


#_POOL_OPT = {'pseudo', 'independent'}
#_CHIM_OPT = {'pooled', 'consensus', 'none'}

plugin = qiime2.plugin.Plugin(
    name='SpiecEasi',
    version=q2_SpiecEasi.__version__,
    website='https://github.com/zdk123/SpiecEasi/',
    package='q2_SpiecEasi',
    description=('This QIIME 2 plugin wraps SpiecEasi '
                 'and will be useful to anybody who wants to infer graphical models'
                 'for all sorts of compositional data, though primarily intended for'
                 'microbiome relative abundance data (generated from 16S amplicon sequence data).'),
    short_description='A QIIME 2 plugin to expose some SpiecEasi functionality..',
    #citations=qiime2.plugin.Citations.load('citations.bib', package='q2_dada2'
)



plugin.methods.register_function(
    function=q2_SpiecEasi.SpiecEasi,
    inputs={'table', FeatureTable[Frequency]},
    parameters={'--method':qiime2.plugin.str,
               '--lambda.min.ratio': qiime2.plugin.Float,
               '--nlambda': qiime2.plugin.Int,
               '--rep.num': qiime2.plugin.Int,
               },
        
    outputs=[('matrix', NetworkFormat)],
    input_descriptions={
        'table': ('All sorts of compositional data'
                               'though primarily intended for microbiome relative abundance data'
                               '(generated from 16S amplicon sequence data)')
    },
    parameter_descriptions={
        'method': ('Methods available for spieceasi,for example mb,glasso,slr'),
        'lambda.min.ratio': ('Input parameter of spieceasi which represents the scaling factor'
                             'that determines the minimum sparsity/lambda parameter'),
        'nlambda': ('Input parameter of spieceasi '),
        'rep.num': ('Input parameter of spieceasi ')
    }
    output_descriptions={
        'table': 'The resulting feature table.',
        'representative_sequences': ('The resulting feature sequences. Each '
                                     'feature in the feature table will be '
                                     'represented by exactly one sequence.')
    },
    name='SpiecEasi',
    description=('This method generates the sparse matrix of network of input data')
)

plugin.register_formats(NetworkFormat)
plugin.register_semantic_types(NetworkFormat)
plugin.register_semantic_type_to_format(NetworkFormat)
importlib.import_module('q2_SpiecEasi._transformer')