#!/usr/bin/env python3
'''
CPSC 415 -- Homework #3 support file
Stephen Davies, University of Mary Washington, fall 2021
'''

import builtins
import chess_config
from chess_model import Board

size = input("Size of board? (mini, reg, large) ")
crazy = input("Crazy mode? (True, False) ")

builtins.cfg = chess_config.Config(size, crazy)

b = Board()
b._reset()

square = input("What square to examine? (or 'done') ")
while square != "done":
    if square in b:
        print(f"    There is {b[square]} on {square}.")
    else:
        print(f"    There is no piece on {square}.")
    square = input("What square to examine? (or 'done') ")

print("Here are all the pieces on this board:")
for square in b:
    print(f"    There is {b[square]} on {square}.")
