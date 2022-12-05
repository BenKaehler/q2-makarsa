import tempfile
import subprocess
from pathlib import Path
from networkx import read_graphml, Graph
import pandas as pd
import networkx as nx
from operator import itemgetter
import pickle
import os


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
        ncores: int = 1,
        thresh: float = 0.05,
        subsample_ratio: float = 0.8,
        seed: float = None,
        sel_criterion: str = 'stars',
        verbose: bool = False,
        pulsar_select: bool = True,
        lambda_log: bool = True,
        lambda_min: float = -1,
        lambda_max: float = -1) -> Graph:

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        table_file = temp_dir / 'input-data.tsv'
        network_file = temp_dir / 'network.mtx'
        # EEE would be better to save as a biom
        table.to_csv(str(table_file), sep='\t')

        cmd = ['run_SpiecEasi.R',
               '--input-file', str(table_file),
               '--output-file', str(network_file),
               '--method', method,
               '--lambda-min-ratio', str(lambda_min_ratio),
               '--nlambda', str(nlambda),
               '--rep-num', str(rep_num),
               '--ncores', str(ncores),
               '--thresh', str(thresh),
               '--subsample-ratio', str(subsample_ratio),
               '--sel-criterion', str(sel_criterion)]

        if verbose:
            cmd.append('--verbose')
        if not lambda_log:
            cmd.append('--not-lambda-log')
        if not pulsar_select:
            cmd.append('--not-pulsar_select')

        if seed is not None:
            cmd.extend(['--seed', str(seed)])

        if not lambda_log:
            if lambda_max > 0:
                cmd.extend(['--lambda-max', str(lambda_max)])
            if lambda_min >= 0:
                cmd.extend(['--lambda-min', str(lambda_min)])

        try:
            run_commands([cmd])
        except subprocess.CalledProcessError as e:
            raise Exception(
                    "An error was encountered while running SpiecEasi"
                    f" in R (return code {e.returncode}), please inspect "
                    "stdout and stderr to learn more.")

        # EEE would be better to return this without reading it
        return read_graphml(str(network_file))
    
    


def statistic_of_network(network):
    
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        tmp_sorted_degree_centrality = os.path.join(temp_dir, 'sorted_degree_centrality')
        tmp_sorted_betweenness_centrality = os.path.join(temp_dir, 'sorted_betweenness_centrality')
        tmp_sorted_closeness_centrality = os.path.join(temp_dir, 'sorted_closeness_centrality')
        tmp_sorted_eigenvector_centrality = os.path.join(temp_dir, 'sorted_eigenvector_centrality')
        tmp_sorted_associativity = os.path.join(temp_dir, 'sorted_associativity')

        sorted_degree_centrality=sorted(nx.degree_centrality(net).items(),key=itemgetter(1), reverse=True)
        pickle.dump(sorted_degree_centrality,open('tmp_sorted_degree_centrality','wb'))
        sorted_betweenness_centrality=sorted(nx.betweenness_centrality(net).items(),key=itemgetter(1),reverse=True)
        pickle.dump(sorted_betweenness_centrality,open('tmp_sorted_betweenness_centrality','wb'))
        sorted_closeness_centrality=sorted(nx.closeness_centrality(net).items(),key=itemgetter(1),reverse=True)
        pickle.dump(sorted_closeness_centrality,open('tmp_sorted_closeness_centrality','wb'))
        sorted_eigenvector_centrality=sorted(nx.eigenvector_centrality(net).items(),key=itemgetter(1),reverse=True)
        pickle.dump(sorted_eigenvector_centrality,open('tmp_sorted_eigenvector_centrality','wb'))
        sorted_associativity=sorted(nx.assortativity.average_neighbor_degree(net).items(),key=lambda e: e[1], reverse=True)
        pickle.dump(sorted_associativity,open('tmp_sorted_associativity','wb'))
        
        #nx. assortativity.average_neighbor_degree(),calculates, for each node, an average of its neighbor’s degrees.
        return(tmp_sorted_degree_centrality,tmp_sorted_betweenness_centrality,tmp_sorted_closeness_centrality,tmp_sorted_eigenvector_centrality,tmp_sorted_associativity)



