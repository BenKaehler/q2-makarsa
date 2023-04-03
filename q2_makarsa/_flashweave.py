import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import qiime2
from networkx import Graph, read_gml, set_node_attributes

from ._run_commands import run_commands


def flashweave(
    table: pd.DataFrame,
    meta_data: qiime2.Metadata = None,
    # defaults copied from FlashWeave.jl/src/learning.jl
    heterogeneous: bool = False,
    sensitive: bool = True,
    max_k: int = 3,
    alpha: float = 0.01,
    conv: float = 0.01,
    feed_forward: bool = True,
    max_tests: int = 1000000,
    hps: int = 5,
    fdr: bool = True,
    n_obs_min: int = -1,
    time_limit: float = -1.,
    normalize:  bool = True,
    track_rejections: bool = False,
    prec: int = 64,
    make_sparse: bool = True,
    update_interval: float = 30,
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
            "--max_k",
            str(max_k),
            "--alpha",
            str(alpha),
            "--conv",
            str(conv),
            "--max_tests",
            str(max_tests),
            "--hps",
            str(hps),
            "--n_obs_min",
            str(n_obs_min),
            "--time_limit",
            str(time_limit),
            "--prec",
            str(prec),
            "--update_interval",
            str(update_interval),
            "--verbose"
        ]
        if meta_data:
            meta_data = meta_data.to_dataframe()
            meta_data_file = temp_dir / "meta-input-data.tsv"
            meta_data.to_csv(str(meta_data_file), sep="\t")
            cmd += [
                "--metadatapath",
                str(meta_data_file),
            ]

        flags = (
            (heterogeneous, "--heterogeneous"),
            (sensitive, "--sensitive"),
            (feed_forward, "--feed_forward"),
            (fdr, "--FDR"),
            (normalize, "--normalize"),
            (track_rejections, "--track_rejections"),
            (make_sparse, "--make_sparse")
        )
        cmd += [f for v, f in flags if v]

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
