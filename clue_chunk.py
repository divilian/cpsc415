#!/usr/bin/env python3
'''
CPSC 415 -- Homework #5 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

import sys
from pathlib import Path
import json
from clue import Clue, get_player_class
from collections import Counter
import logging

def print_usage():
    print('Usage: clue_chunk.py netId1 netId2 netId3 num_games.')

if len(sys.argv) != 5  or  any(['usage' in x for x in sys.argv]):
    print_usage()
    sys.exit(1)

this_module = sys.modules[__name__]

logging.basicConfig(level=logging.CRITICAL)

player_classes = [ get_player_class(c) for c in sys.argv[1:4] ]
clue = Clue(player_classes)
wins = Counter()
for _ in range(int(sys.argv[4])):
    wins[str(clue.play())] += 1
print(json.dumps(wins))
