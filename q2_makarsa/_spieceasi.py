import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from networkx import Graph, read_graphml

from ._run_commands import run_commands


def spiec_easi(
    table: pd.DataFrame,
    method: str = "glasso",
    lambda_min_ratio: float = 1e-3,
    nlambda: int = 20,
    rep_num: int = 20,
    ncores: int = 1,
    thresh: float = 0.05,
    subsample_ratio: float = 0.8,
    seed: float = None,
    sel_criterion: str = "stars",
    verbose: bool = False,
    pulsar_select: bool = True,
    lambda_log: bool = True,
    lambda_min: float = -1,
    lambda_max: float = -1,
) -> Graph:

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        table_file = temp_dir / "input-data.tsv"
        network_file = temp_dir / "network.mtx"
        # EEE would be better to save as a biom
        table.to_csv(str(table_file), sep="\t")

        cmd = [
            "run_SpiecEasi.R",
            "--input-file",
            str(table_file),
            "--output-file",
            str(network_file),
            "--method",
            method,
            "--lambda-min-ratio",
            str(lambda_min_ratio),
            "--nlambda",
            str(nlambda),
            "--rep-num",
            str(rep_num),
            "--ncores",
            str(ncores),
            "--thresh",
            str(thresh),
            "--subsample-ratio",
            str(subsample_ratio),
            "--sel-criterion",
            str(sel_criterion),
        ]

        if verbose:
            cmd.append("--verbose")
        if not lambda_log:
            cmd.append("--not-lambda-log")
        if not pulsar_select:
            cmd.append("--not-pulsar_select")

        if seed is not None:
            cmd.extend(["--seed", str(seed)])

        if not lambda_log:
            if lambda_max > 0:
                cmd.extend(["--lambda-max", str(lambda_max)])
            if lambda_min >= 0:
                cmd.extend(["--lambda-min", str(lambda_min)])

        try:
            run_commands([cmd])
        except subprocess.CalledProcessError as e:
            raise Exception(
                "An error was encountered while running SpiecEasi"
                f" in R (return code {e.returncode}), please inspect "
                "stdout and stderr to learn more."
            )

        # EEE would be better to return this without reading it
        return read_graphml(str(network_file))
