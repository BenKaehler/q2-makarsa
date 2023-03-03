
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from networkx import Graph, read_graphml


def run_commands(cmds, verbose=True):
    if verbose:
        print(
            "Running external command line application(s). This may print "
            "messages to stdout and/or stderr."
        )
        print(
            "The command(s) being run are below. These commands cannot "
            "be manually re-run as they will depend on temporary files that "
            "no longer exist."
        )
    for cmd in cmds:
        if verbose:
            print("\nCommand:", end=" ")
            print(" ".join(cmd), end="\n\n")
        subprocess.run(cmd, check=True)


def flashweave(
    table: pd.DataFrame,
    meta_table: pd.DataFrame,
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
        meta_table_file=temp_dir / "meta-input-data.tsv"
        network_file = temp_dir / "network.graphml"
        #table.to_csv(str(table_file), sep="\t")
           #here I just need to pass the path of the input files as flashweave need only input path.
        cmd = [
            "julia",
            "run_FlashWeave.jl",
            "--input-file",
            str(table_file),
            "--meta-input-file",
            str(meta_table_file),
            "--output-file",
            str(network_file),
            "--min-cluster-size",
            str(min_cluster_size),
            "--max-cluster-size",
            str(max_cluster_size),
            "--pca_dimension",
            str(pca_dimension),
            "--seed",
            str(seed),
            "--alpha",
            str(alpha),
            "--nruns",
            str(nruns),
            "--subsample-ratio",
            str(subsample_ratio),
            "--num-clusters",
            str(num_clusters),
            "--max-overlap",
            str(max_overlap),
            
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

        return read_graphml(str(network_file))



