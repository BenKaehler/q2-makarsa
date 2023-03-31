from networkx import Graph, read_graphml, write_graphml
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin import Bool, Float, Int, Metadata, Plugin, Str
import pandas as pd

from ._network import Network, NetworkDirectoryFormat, NetworkFormat, NodeCommunityFormat, Node_Community, NodeDirectoryFormat
from ._spieceasi import spiec_easi
from ._visualisation import visualise_network
from ._louvain import louvain_communities

plugin = Plugin(
    name="makarsa",
    version="0.0.0-dev",
    website="https://github.com/BenKaehler/q2-makarsa",
    package="q2_makarsa",
    description=(
        "This QIIME 2 plug-in provides biological network analysis and "
        "visualisation and may be useful to anybody who wants to infer "
        "graphical models for all sorts of compositional "
        "data, though primarily intended for microbiome "
        "relative abundance data (generated from 16S "
        "amplicon sequence data)."
    ),
    short_description="A QIIME 2 plugin to expose some SpiecEasi "
    "functionality.",
    # citations=qiime2.plugin.Citations.load(
    #    'citations.bib', package='q2_dada2'
)

plugin.register_semantic_types(Network)
plugin.register_formats(NetworkDirectoryFormat, NetworkFormat)
plugin.register_semantic_type_to_format(
    Network, artifact_format=NetworkDirectoryFormat
)

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
    inputs={"network": Network},
    parameters={"metadata": Metadata},
    name="Visualize network",
    description="Create an interactive depiction of your network.",
)


plugin.methods.register_function(
    function=spiec_easi,
    inputs={"table": FeatureTable[Frequency]},
    parameters={
        "method": Str,
        "lambda_min_ratio": Float,
        "nlambda": Int,
        "rep_num": Int,
        "ncores": Int,
        "thresh": Float,
        "subsample_ratio": Float,
        "seed": Float,
        "sel_criterion": Str,
        "verbose": Bool,
        "pulsar_select": Bool,
        "lambda_log": Bool,
        "lambda_min": Float,
        "lambda_max": Float,
    },
    outputs=[("network", Network)],
    input_descriptions={
        "table": (
            "All sorts of compositional data though primarily intended "
            "for microbiome relative abundance data "
            "(generated from 16S amplicon sequence data)"
        )
    },
    parameter_descriptions={
        "method": "Methods available for spieceasi,for example mb,glasso,slr",
        "lambda_min_ratio": (
            "Input parameter of spieceasi which represents "
            "the scaling factor that determines the minimum "
            "sparsity/lambda parameter"
        ),
        "nlambda": "Input parameter of spieceasi ",
        "rep_num": "Input parameter of spieceasi ",
        "ncores": "Number of cores for parallel computation",
        "thresh": "Threshold for StARS criterion",
        "subsample_ratio": "Subsample size for StARS",
        "seed": "Set the random seed for subsample set",
        "sel_criterion": "Specifying criterion/method for model selection, "
        "Accepts 'stars' [default], 'bstars' (Bounded StARS)",
        "verbose": "Print extra output [default]",
        "pulsar_select": "Perform model selection",
        "lambda_log": "lambda.log should values of lambda be distributed "
        "logarithmically (TRUE) or linearly (FALSE) between "
        "lamba.min and lambda.max",
    },
    output_descriptions={"network": "The inferred network"},
    name="SpiecEasi",
    description=(
        "This method generates the sparse matrix of network of input " "data"
    ),
)

plugin.register_semantic_types(Node_Community)
plugin.register_formats(NodeCommunityFormat, NodeDirectoryFormat)
plugin.register_semantic_type_to_format(
    Node_Community, artifact_format=NodeDirectoryFormat
)




@plugin.register_transformer
def _3(community_out: pd.DataFrame) -> NodeCommunityFormat:
    ff = NodeCommunityFormat()
    community_out.to_csv(str(ff), sep='\t', index=False)
    return ff

plugin.methods.register_function(
    function=louvain_communities,
    inputs={"network_input": Network},
    parameters={
        "num_partitions": Int,
        "remove_neg": Bool,
        "seed": Int
        },
    outputs=[("community_out", Node_Community)],
    input_descriptions={
        'network_input': ('OTU co-ocurrence or co-abbundance network')
    },
    parameter_descriptions={
        'num_partitions': 'Number of partitions to use to obatin the consensus.',
        'remove_neg': 'Remove negative edges from the network [Default uses absolute value].',
        'seed': 'Seed value for deterministic result.'
    },
    output_descriptions={'community_out': ('output file containing network nodes and their respective communities.')},
    name='Louvain Community Detection',
    description=("Obtain the consensus community partition of an OTU co-ocurrence"
                 " or co-abbundance network using the louvain algorithm."),

)