#!/usr/bin/env python3


import os
import tempfile
import hashlib
import subprocess

import biom
import skbio
import qiime2.util
import pandas as pd



def run_commands(cmds, verbose=True):
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
        subprocess.run(cmd, check=True, shell=True)

        


        
        

def _q2_SpiecEasi(input_data,output_file, method,lambda_min_ratio,nlambda,rep_num):
   
   
    #with tempfile.TemporaryDirectory() as temp_dir_name:
       # biom_fp = os.path.join(temp_dir_name, 'output.tsv.biom')
       # track_fp = os.path.join(temp_dir_name, 'track.tsv')

        cmd = ['run_SpiecEasi.R',
               '--input_file', str(input_data),
               '--output_file', str(output_file),
               '--method', str(method),
               '--lambda.min.ratio', str(lambda_min_ratio),
               '--nlambda', str(nlambda),
               '--rep.num', str(rep_num)]
        
        try:
            run_commands([cmd])
        except subprocess.CalledProcessError as e:
            if e.returncode == 2:
                raise ValueError(
                    "No reads passed the filter. trunc_len (%r) may be longer"
                    " than read lengths, or other arguments (such as max_ee"
                    " or trunc_q) may be preventing reads from passing the"
                    " filter." )
            else:
                raise Exception("An error was encountered while running SpiecEasi"
                                " in R (return code %d), please inspect stdout"
                                " and stderr to learn more.")
        return _q2_SpiecEasi(output_file)