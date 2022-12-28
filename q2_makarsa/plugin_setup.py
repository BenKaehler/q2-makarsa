from networkx import Graph, read_graphml, write_graphml
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin import Bool, Float, Int, Metadata, Plugin, Str

from ._network import Network, NetworkDirectoryFormat, NetworkFormat
from ._spieceasi import spiec_easi
from ._stats import annotate_node_stats
from ._visualisation import visualise_network

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

plugin.methods.register_function(
    function=annotate_node_stats,
    inputs={"network": Network},
    parameters={},
    outputs=[("network", Network)],
    input_descriptions={"network": "The inferred network from SpiecEasi."},
    output_descriptions={
        "network": "Network with node attributes. Here we assign each node "
        "with their degree centrality, betweenness centrality, closeness "
        "centrality, eigenvector centrality and associativity as attribute."
    },
    name="network with attribute",
    description=(
        "Update the network with different centrality as node attribute."
    ),
)
