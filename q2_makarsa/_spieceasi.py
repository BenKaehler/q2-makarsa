import subprocess
import tempfile
from pathlib import Path

from networkx import Graph, read_graphml
import biom
import qiime2 as q2
import numpy as np
from sklearn.preprocessing import OneHotEncoder

from ._run_commands import run_commands


def encode_metadata(sample_ids, metadata, metadata_column):
    encoded_metadata = []
    for column in metadata.columns:
        if metadata_column and column not in metadata_column:
            continue
        values = metadata.get_column(column)

        is_numeric = isinstance(values, q2.NumericMetadataColumn)
        values = values.to_dataframe()
        values = values.loc[sample_ids]
        if is_numeric:
            values = values >= values.iloc[:, 0].median()
            values = values.replace({True: "High", False: "Low"})

        encoder = OneHotEncoder(sparse=False)
        encoded = encoder.fit_transform(values)
        columns = [f"{column} {c}" for c in encoder.categories_[0]]
        # At this stage it would be nice to drop one of the columns
        # if there are only two states, but the SpiecEasi normalization
        # step fails if there is only one column.
        # if len(columns) == 2:
        #     encoded = encoded[:, 1].reshape(-1, 1)
        #     columns = [columns[1]]

        # Zeroes make the CLR transform in SpiecEasi fail.
        # Instead transform them so that post-CLR, the values
        # have (empirical) mean zero and variance of one.
        for i in range(encoded.shape[0]):
            D = encoded.shape[1]
            D1 = encoded[i].sum()
            D0 = D - D1
            zero_idx = encoded[i] == 0.
            ones_idx = np.logical_not(zero_idx)
            # Subtract 1 to correct for the SpiecEasi pseudocount
            encoded[i][ones_idx] = np.exp(D / np.sqrt(D0 * D1)) - 1
        encoded = biom.Table(
            encoded.T, sample_ids=values.index, observation_ids=columns)

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
    metadata_column: list = None,
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
            sample_ids = one_table.ids(axis='sample')
        if metadata:
            metadata_tables = encode_metadata(
                sample_ids, metadata, metadata_column)
            metadata_columns = []
            for i, one_table in enumerate(metadata_tables, i + 1):
                table_files.append(write_table(i, temp_dir, one_table))
                metadata_columns.extend(one_table.ids(axis='observation'))
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

        graph = read_graphml(str(network_file))
        if metadata:
            for node in graph.nodes:
                graph.nodes[node]["mv"] = \
                    graph.nodes[node]["Feature"] in metadata_columns
        return graph
