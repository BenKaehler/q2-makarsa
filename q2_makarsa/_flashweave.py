import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from networkx import Graph, read_gml, set_node_attributes

from ._run_commands import run_commands


def flashweave(
    table: pd.DataFrame,
    # not sure if the following conversion happens automagically
    meta_data: pd.DataFrame = None,
    min_cluster_size: int = 2,
    max_cluster_size: int = 50,
    pca_dimension: int = 10,
    n_threads: int = 1,
    seed: int = 42,
    alpha: float = 0.05,
    nruns: int = 10,
    subsample_ratio: float = 0.8,
    num_clusters: int = 15,
    max_overlap: float = 0.8,
    verbose: bool = False,
) -> Graph:

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        table_file = temp_dir / "input-data.tsv"
        network_file = temp_dir / "network.gml"
        table.to_csv(str(table_file), sep="\t")
        cmd = [
            "run_FlashWeave.jl",
            "--datapath",
            str(table_file),
            "--output",
            str(network_file),
            "--minclustersize",
            str(min_cluster_size),
            "--maxclustersize",
            str(max_cluster_size),
            "--pcadimension",
            str(pca_dimension),
            "--nthreads",
            str(n_threads),
            "--seed",
            str(seed),
            "--alpha",
            str(alpha),
            "--nruns",
            str(nruns),
            "--subsampleratio",
            str(subsample_ratio),
            "--numclusters",
            str(num_clusters),
            "--maxoverlap",
            str(max_overlap)
        ]
        if meta_data:
            meta_data_file = temp_dir / "meta-input-data.tsv"
            meta_data.to_csv(str(meta_data_file), sep="\t")
            cmd += [
                "--metadatapath",
                str(meta_data_file),
            ]
        if verbose:
            cmd.append("--verbose")

        try:
            run_commands([cmd])
        except subprocess.CalledProcessError as e:
            raise Exception(
                "An error was encountered while running FlashWeave"
                f" in Julia (return code {e.returncode}), please inspect "
                "stdout and stderr to learn more."
            )

        network = read_gml(str(network_file))

    # SpiecEasi puts the feature id in a Feature attribute,
    # so let's do the same thing here.
    attributes = {}
    for nid, attr in network.nodes(data=True):
        attributes[nid] = {"Feature": nid}
    set_node_attributes(network, attributes)

    return network
