'''
CPSC 415 -- Program #1 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

import importlib
import subprocess
import math
import os
import sys
from functools import reduce
import operator
import itertools
import logging
import random
from collections import namedtuple
import pandas as pd
import statistics
import glob

from vacuum import *

Result = namedtuple('Result','score num_steps')

class Suite():

    NUM_CORES = 12

    def __init__(self, base_seed=0, num_seeds=10):
        self.base_seed = base_seed
        self.num_seeds = num_seeds

    def run(self, userid, max_steps=10000):
        try:
            stud_module = importlib.import_module(userid + '_vacuum')
            vacuum_class = getattr(stud_module,userid.capitalize() +
                'VacuumAgent')
        except Exception as err:
            print(str(err))
            sys.exit(2)
        num_runs_per_core = math.ceil(self.num_seeds / self.NUM_CORES)
        starting_seeds_for_core = [ self.base_seed + i*num_runs_per_core 
            for i in range(self.NUM_CORES) ]
        procs = []
        output_files = []
        for start_seed in starting_seeds_for_core:
            ending_seed = min(self.base_seed + self.num_seeds - 1, 
                start_seed + num_runs_per_core - 1)
            logging.info('Running seeds {}-{}...'.format(start_seed,
                ending_seed))
            output_file = 'output{}.csv'.format(start_seed)
            cmd_line = ['python3','./chunk_vacuum.py', userid, '{}-{}'.format(
                start_seed, ending_seed), str(max_steps) ]
            procs.append(subprocess.Popen(cmd_line))
            output_files.append(output_file)

        print('Waiting for completion...')
        [ p.wait() for p in procs ]
        print('...done.')

        results = pd.DataFrame({'seed':[],'score':[],'num_steps':[]})
        results = pd.concat([ pd.read_csv(ofile, encoding="utf-8")
            for ofile in output_files ])

        scores = results['score']
        steps = results['num_steps']
        with open(f'output_{userid}.csv','w',encoding="utf-8") as f:
            print('# Score: min {}, max {}, med {}'.format(min(scores),
                max(scores), int(statistics.median(scores))))
            print('# Num steps: min {}, max {}, med {}'.format(min(steps),
                max(steps), int(statistics.median(steps))))
            print('# Score: min {}, max {}, med {}'.format(min(scores),
                max(scores), int(statistics.median(scores))), file=f)
            print('# Num steps: min {}, max {}, med {}'.format(min(steps),
                max(steps), int(statistics.median(steps))), file=f)
        results.to_csv(f"output_{userid}.csv",mode="a",encoding="utf-8",
            index=None)
        print(f'Output in output_{userid}.csv.')
        for ofile in glob.glob('output[0-9]*.csv'):
            os.remove(ofile)
        med = statistics.median(scores)
        if med > 5000:
            print("\n{} earned +50XP! (the max)".format(userid))
        elif med < 0:
            print("\n{} earned +0XP, sorry!".format(userid))
        else:
            print("\n{} earned +{}XP!".format(userid,math.ceil(med / 100)))
