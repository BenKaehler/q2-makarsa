from networkx import Graph, read_graphml, write_graphml
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin import Bool, Float, Int, Metadata, Plugin, Str, List

from ._network import Network, NetworkDirectoryFormat, NetworkFormat
from ._spieceasi import spiec_easi
from ._flashweave import flashweave
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
    short_description=(
        "A QIIME 2 plugin to expose some SpiecEasi functionality."
    ),
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
    inputs={"table": List[FeatureTable[Frequency]]},
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
        "sel_criterion": (
            "Specifying criterion/method for model selection, "
            "Accepts 'stars' [default], 'bstars' (Bounded StARS)"
        ),
        "pulsar_select": "Perform model selection",
        "lambda_log": (
            "lambda.log should values of lambda be distributed "
            "logarithmically (TRUE) or linearly (FALSE) between "
            "lamba.min and lambda.max"
        ),
    },
    output_descriptions={"network": "The inferred network"},
    name="SpiecEasi",
    description=(
        "This method generates the sparse matrix of network of input data"
    ),
)


plugin.methods.register_function(
    function=flashweave,
    inputs={"table": FeatureTable[Frequency]},
    parameters={
        "meta_data": Metadata,
        "heterogeneous": Bool,
        "sensitive": Bool,
        "max_k": Int,
        "alpha": Float,
        "conv": Float,
        "feed_forward": Bool,
        "max_tests": Int,
        "hps": Int,
        "fdr": Bool,
        "n_obs_min": Int,
        "time_limit": Float,
        "normalize": Bool,
        "track_rejections": Bool,
        "prec": Int,
        "make_sparse": Bool,
        "update_interval": Float,
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
        "meta_data": "a path which contain file of meta data of input data",
        "heterogeneous": (
            "enable heterogeneous mode for multi-habitat or"
            "-protocol data with at least thousands of samples"
            "(FlashWeaveHE), default = false"
        ),
        "sensitive": (
            "enable fine-grained associations(FlashWeave-S,FlashWeaveHE-S),"
            "sensitive=false results in the fast modes FlashWeave-F"
            "or FlashWeaveHE-F,default = true"
        ),
        "max_k": (
            "maximum size of conditioning sets, high values can"
            " stronglyincrease runtime. max_k=0 results in no conditioning"
            " (univariate mode)"
        ),
        "alpha": "threshold used to determine statistical significance",
        "conv": (
            "convergence threshold, i.e. if conv=0.01 assume convergence if"
            " the numberof edges increased by only 1% after 100% more runtime"
            " (checked in intervals)"
        ),
        "feed_forward": "enable feed-forward heuristic,default = true ",
        "max_tests": (
            "maximum number of conditional tests that should be performed"
            "on a variable pair before association is assumed"
        ),
        "hps": (
            "reliability criterion for statistical tests when sensitive=false"
        ),
        "fdr": (
            "perform False Discovery Rate correction (Benjamini-Hochberg"
            " method)on pairwise associations, default = true"
        ),
        "n_obs_min": (
            "don't compute associations between variables having less reliable"
            " samples(i.e. non-zero if heterogeneous=true) than this number."
            " -1: automatically choose a threshold"
        ),
        "time_limit": (
            "if feed-forward heuristic is active,determines the"
            " interval(seconds)at which neighborhood information is updated"
        ),
        "normalize": (
            "automatically choose and perform data normalization"
            "(based on sensitive and heterogeneous), default = true"
        ),
        "track_rejections": (
            "store for each discarded edge, which variable set lead to its"
            " exclusion(can be memory intense for large networks), default ="
            " false"
        ),
        "prec": (
            "precision in bits to use for calculations (16, 32, 64 or 128)"
        ),
        "make_sparse": (
            "use a sparse data representation (should be left at true in"
            " almost all cases),default = true"
        ),
        "update_interval": (
            "if verbose=true, determines the interval (seconds) at which"
            " network stat updates are printed"
        ),
    },
    output_descriptions={"network": "The inferred network"},
    name="flashweave",
    description=(
        "FlashWeave predicts ecological interactions between microbes from "
        "large-scale compositional abundance data "
    ),
)
