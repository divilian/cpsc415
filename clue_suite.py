#!/usr/bin/env python3
'''
CPSC 415 -- Homework #5 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

import sys
import builtins
import subprocess
import json
import operator
from collections import Counter

def print_usage():
    print('Usage: clue_suite.py netId1 netId2 netId3 num_games.')

if len(sys.argv) != 5  or  any(['usage' in x for x in sys.argv]):
    print_usage()
    sys.exit(1)

GAMES_PER_CHUNK = 1000

print(f"Starting {sys.argv[4]}-game match between {sys.argv[1]}, "
    f"{sys.argv[2]}, and {sys.argv[3]}...")
procs = []
num_chunks = max(int(sys.argv[4]) // GAMES_PER_CHUNK,1)
for chunk_num in range(1,num_chunks+1):
    print(f"Starting chunk {chunk_num} of {num_chunks}...")
    procs.append(subprocess.Popen([ 'python3', 'clue_chunk.py',
        sys.argv[1], sys.argv[2], sys.argv[3],
        str(min(GAMES_PER_CHUNK, int(sys.argv[4]))) ],
        encoding="utf-8", stdout=subprocess.PIPE))
print('Waiting for completion...')
[ p.wait() for p in procs ]
print('...done.')
grand_results = Counter()
for p in procs:
    results = json.loads(p.stdout.read())
    grand_results += results
sorted_res = dict(sorted(grand_results.items(),
    key=operator.itemgetter(1), reverse=True))
for k,v in sorted_res.items():
    print(f"{k}: {v} wins ({v/float(sys.argv[4])*100:.1f}%)")

