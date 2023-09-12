import subprocess
import tempfile
from pathlib import Path

from networkx import Graph, read_graphml
import biom
import qiime2 as q2
import numpy as np
from sklearn.preprocessing import OneHotEncoder

from ._run_commands import run_commands


def encode_metadata(metadata):
    encoded_metadata = []
    for column in metadata.columns():
        values = metadata.get_column()

        if isinstance(values, q2.CategoricalMetadataColumn):
            values = q2.to_dataframe()
        elif isinstance(values, q2.NumericalMetadataColumn):
            values = q2.to_dataframe()
            values = values >= values[0].median()
            values.columns[0] = f"{values.columns[0]} High"

        encoder = OneHotEncoder(sparse=False)
        encoded = encoder.fit_transform(values)
        columns = [f"{column} {c}" for c in encoder.categories_[0]]
        if len(columns) == 2:
            encoded = encoded[:, 1]
            columns = columns[1]
        # Zeroes make the CLR transform (in SpiecEasi) fail.
        # Instead transform them so that post-CLR, the values
        # have (empirical) mean zero and variance of one.
        for i in range(encoded.shape[1]):
            D = encoded.shape[0]
            D1 = encoded[:, i].sum()
            D0 = D - D1
            zero_idx = encoded[:, i] == 0.
            ones_idx = np.logical_not(zero_idx)
            encoded[:, i][zero_idx] = 1.
            encoded[:, i][ones_idx] = np.exp(D / np.sqrt(D0 * D1))
        encoded = biom.Table(
            encoded, sample_ids=values.index, observation_ids=columns)

        encoded_metadata.append(encoded)
    return encoded_metadata


def write_table(i, directory, table):
    table_file = str(directory / f"input-data-{i}.biom")
    with biom.util.biom_open(table_file, 'w') as fh:
        table.to_hdf5(fh, 'dummy')
    return table_file


def spiec_easi(
    table: biom.Table,
    metadata: q2.Metadata = None,
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
            table_files.append(write_table(i, temp_dir, one_table))
        if metadata:
            metadata_tables = encode_metadata(metadata)
            for i, one_table in enumerate(metadata_tables, i + 1):
                table_files.append(write_table(i, temp_dir, one_table))
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
