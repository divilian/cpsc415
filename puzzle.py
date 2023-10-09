'''
CPSC 415 -- Homework #2.667 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

import numpy as np
import math
import sys
import time
from copy import deepcopy

np.set_printoptions(linewidth=99999)


class Puzzle():

    def __init__(self, n, grid=None):
        """
        Create an nxn sliding-block puzzle. If grid is None, the configuration
        will actually be a solved Puzzle. not None, it should be a
        2-dimensional matrix of the correct size, with an initial
        configuration.
        """
        self.n = n
        if grid:
            self.grid = grid.copy()
        else:
            self.grid = self._gen_solution()

    @classmethod
    def gen_random_puzzle(cls, n, seed=123):
        """
        Create an nxn random sliding-block puzzle.
        """
        np.random.seed(seed)
        new_puzzle = Puzzle(n)
        NUM_RANDOM_MOVES = 50    # Should be enough I reckon.
        for _ in range(NUM_RANDOM_MOVES):
            new_puzzle._make_a_coupla_random_moves()
        return new_puzzle

    def _gen_solution(self):
        x = np.empty(shape=(self.n,self.n), dtype=int)
        for i in range(self.n**2-1):
            x[i//self.n, i%self.n] = i+1
        x[self.n-1][self.n-1] = -1
        return x

    def legal_moves(self):
        empty_sq = np.where(self.grid == -1)    # could cache this
        moves = []
        if empty_sq[0] > 0:
            moves += ["U"]
        if empty_sq[0] < self.n-1:
            moves += ["D"]
        if empty_sq[1] > 0:
            moves += ["L"]
        if empty_sq[1] < self.n-1:
            moves += ["R"]
        return moves

    def move(self, the_move):
        """
        Return True if the move worked, otherwise False.
        """
        if the_move not in self.legal_moves():
            return False     # Illegal move {the_move}!
        e_sq = np.where(self.grid == -1)    # could cache this
        if the_move == "L":
            self.grid[e_sq[0],e_sq[1]] = self.grid[e_sq[0],e_sq[1]-1]
            self.grid[e_sq[0],e_sq[1]-1] = -1
        elif the_move == "U":
            self.grid[e_sq[0],e_sq[1]] = self.grid[e_sq[0]-1,e_sq[1]]
            self.grid[e_sq[0]-1,e_sq[1]] = -1
        elif the_move == "R":
            self.grid[e_sq[0],e_sq[1]] = self.grid[e_sq[0],e_sq[1]+1]
            self.grid[e_sq[0],e_sq[1]+1] = -1
        else:
            self.grid[e_sq[0],e_sq[1]] = self.grid[e_sq[0]+1,e_sq[1]]
            self.grid[e_sq[0]+1,e_sq[1]] = -1
        return True

    def _make_a_coupla_random_moves(self):
        worked = False
        while not worked:
            direction = np.random.choice(list(self.legal_moves()))
            worked = self.move(direction)
            if worked:
                self.move(direction)   # Try two in a row for more mixup

    def is_solved(self):
        """
        Return True only if this puzzle is actually completed.
        """
        return np.allclose(self.grid, self._gen_solution())

    def has_solution(self, solution):
        me = deepcopy(self)
        for move in solution:
            me.move(move)
        return me.is_solved()
        
    def verify_visually(self, solution):
        for move in solution:
            print(self)
            time.sleep(.25)
            self.move(move)
        print(self)

    def __eq__(self, other):
        return np.all(self.grid == other.grid)

    def __str__(self):
        num_digs = math.ceil(math.log(self.n**2 + 1, 10))
        retval = ''.join(['-']*((num_digs+1)*self.n+1)) + "\n"
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i,j] > 0:
                    retval += f"|{self.grid[i,j]:{num_digs}}"
                else:
                    retval += f"|" + ''.join([' ']*num_digs)
            retval += "|\n"
        retval += ''.join(['-']*((num_digs+1)*self.n+1))
        return retval
