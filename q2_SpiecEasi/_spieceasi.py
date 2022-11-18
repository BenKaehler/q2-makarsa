import tempfile
import subprocess
from pathlib import Path

from networkx import read_graphml, Graph

import pandas as pd


def run_commands(cmds, verbose=True):  # EEE need to credit the authors of this
    if verbose:
        print("Running external command line application(s). This may print "
              "messages to stdout and/or stderr.")
        print("The command(s) being run are below. These commands cannot "
              "be manually re-run as they will depend on temporary files that "
              "no longer exist.")
    for cmd in cmds:
        if verbose:
            print("\nCommand:", end=' ')
            print(" ".join(cmd), end='\n\n')
        subprocess.run(cmd, check=True)


def spiec_easi(
        table: pd.DataFrame,
        method: str = 'glasso',
        lambda_min_ratio: float = 1e-3,
        nlambda: int = 20,
        rep_num: int = 20,
        ncores: int= 1,
        thresh: float = 0.05,
        subsample_ratio: float = 0.8,
        seed: str = None,
        wkdir: str = None,
        regdir: str = None,
        init: str = 'init',
        conffile: str = None,
        jobres: float = [],
        cleanup: bool = False,
        selcriterion: str = 'stars',
        verbose: bool = True,
        pulsarselect: str = True,
        lambdalog: bool = True) -> Graph:

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        table_file = temp_dir / 'input-data.tsv'
        network_file = temp_dir / 'network.mtx'
        # EEE would be better to save as a biom
        table.to_csv(str(table_file), sep='\t')

        cmd = ['run_SpiecEasi.R',
               '--input_file', str(table_file),
               '--output_file', str(network_file),
               '--method', method,
               '--lambda.min.ratio', str(lambda_min_ratio),
               '--nlambda', str(nlambda),
               '--rep.num', str(rep_num),
               '--ncores', str(ncores),
               '--thresh', str(thresh),
               '--subsample.ratio', str(subsample_ratio),
               '--seed', str(seed),
               '--wkdir', str(wkdir),
               '--regdir', str(regdir),
               '--init', init,
               '--conffile', str(conffile),
               '--job.res', str(jobres),
               '--cleanup', str(cleanup),
               '--sel.criterion', str(selcriterion),
               '--verbose', str(verbose),
               '--pulsar.select', str(pulsarselect),
               '--lambda.log', str(lambdalog)]
        
        try:
            run_commands([cmd])
        except subprocess.CalledProcessError as e:
            raise Exception(
                    "An error was encountered while running SpiecEasi"
                    f" in R (return code {e.returncode}), please inspect "
                    "stdout and stderr to learn more.")

        # EEE would be better to return this without reading it
        return read_graphml(str(network_file))
