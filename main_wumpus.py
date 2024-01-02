#!/usr/bin/env python3
'''
CPSC 415 -- Homework #4 support file
Stephen Davies, University of Mary Washington, fall 2023
'''
import logging
import importlib
import sys
import statistics
import numpy as np

from environment import *
from agent import *
from wumpus import *
from visualize import *


def print_usage():
    print('Usage: main_wumpus.py explorer_name [interactive|auto|suite=#] ' +
        '[seed] [debugLevel|NONE].')

if len(sys.argv) not in [2,3,4,5]:
    print_usage()
    sys.exit(1)

if len(sys.argv) > 2:
    interactive = sys.argv[2] == 'interactive'
    do_suite = sys.argv[2].startswith('suite=')
    if do_suite:
        try:
            num_runs = int(sys.argv[2][sys.argv[2].index('=')+1:])
        except:
            print_usage()
            print("('suite=#' parameter must be numeric.)")
            sys.exit(2)
else:
    interactive = True
    do_suite = False

if len(sys.argv) > 3:
    try:
        seed = int(sys.argv[3])
        if seed == 0:
            seed = random.randrange(10000)
    except:
        print_usage()
        print("('seed' must be numeric.)")
        sys.exit(3)
else:
    seed = random.randrange(10000)

if len(sys.argv) > 4:
    if sys.argv[4] == 'NONE':
        logging.getLogger().setLevel(logging.CRITICAL + 1)
    else:
        logging.getLogger().setLevel(sys.argv[4])
else:
    logging.getLogger().setLevel('CRITICAL')

try:
    stud_module = importlib.import_module(sys.argv[1] + '_ExplorerAgent')
    Explorer_class = getattr(stud_module,sys.argv[1] + '_ExplorerAgent')
except Exception as err:
    print(str(err))
    sys.exit(2)

if not issubclass(Explorer_class, ExplorerAgent):
    print("{} doesn't inherit from ExplorerAgent.".format(
        Explorer_class.__name__))
    sys.exit(3)

# Go!
if do_suite:
    from suite_wumpus import *
    results = Suite(seed,num_runs).run(sys.argv[1])
    print('# Score: min {}, max {}, med {}, mean {}'.format(
        min(results.scores), max(results.scores),
        int(statistics.median(results.scores)),
        np.array(results.scores).mean()))
    print('# Num steps: min {}, max {}, med {}, mean {}'.format(
        min(results.steps), max(results.steps),
        int(statistics.median(results.steps)),
        np.array(results.steps).mean()))
else:
    # Actually instantiate the student's agent.
    explorer = Explorer_class()
    print('Using seed {}.'.format(seed))
    random.seed(seed)
    we = WumpusEnvironment()
    we.add_thing(explorer, we.START_SQUARE)
    ve = VisualXYEnvironment(we, 100, 100, 'Wumpus world')
    ve.start(interactive)
