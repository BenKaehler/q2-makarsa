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
    heterogeneous: bool = False,
    sensitive: bool = False,
    max_k: int = 2,
    alpha: float = 0.05,
    conv: float = 0.01,
    feed_forward: bool = True,
    max_tests: int = 20,
    hps: float = 1.0,
    FDR: bool = False,
    n_obs_min: int = -1,
    time_limit: int = 60,
    normalize:  bool = True,
    track_rejections: bool = False,
    verbose: bool = True,
    transposed: bool = False,
    prec: int = 64,
    make_sparse: bool = True,
    update_interval: int = 10,
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
            "--heterogeneous",
            str(heterogeneous),
            "--sensitive",
            str(sensitive),
            "--max_k",
            str(max_k),
            "--alpha",
            str(alpha),
            "--conv",
            str(conv),
            "--feed_forward",
            str(feed_forward),
            "--max_tests",
            str(max_tests),
            "--hps",
            str(hps),
            "--FDR",
            str(FDR),
            "--n_obs_min",
            str(n_obs_min),
            "--time_limit",
            str(time_limit),
            "--normalize",
            str(normalize),
            "--track_rejections",
            str(track_rejections),
            "--transposed",
            str(transposed),
            "--prec",
            str(prec),
            "--make_sparse",
            str(make_sparse),
            "--update_interval",
            str(update_interval)
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
