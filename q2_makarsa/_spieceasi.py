import subprocess
import tempfile
from pathlib import Path

from networkx import Graph, read_graphml
import biom

from ._run_commands import run_commands


def spiec_easi(
    table: biom.Table,
    method: str = "glasso",
    lambda_min_ratio: float = 1e-3,
    nlambda: int = 20,
    rep_num: int = 20,
    ncores: int = 1,
    thresh: float = 0.05,
    subsample_ratio: float = 0.8,
    seed: float = None,
    sel_criterion: str = "stars",
    pulsar_select: bool = True,
    lambda_log: bool = True,
    lambda_min: float = -1,
    lambda_max: float = -1,
) -> Graph:

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        table_files = []
        for i, one_table in enumerate(table):
            table_file = str(temp_dir / f"input-data-{i}.biom")
            table_files.append(table_file)
            with biom.util.biom_open(table_file, 'w') as fh:
                one_table.to_hdf5(fh, 'dummy')
        table_files = ', '.join(table_files)
        network_file = temp_dir / "network.mtx"

        cmd = [
            "run_SpiecEasi.R",
            "--input-file",
            table_files,
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
            "--verbose"
        ]

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
