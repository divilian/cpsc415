'''
CPSC 415 -- Homework support file
Stephen Davies, University of Mary Washington, fall 2023
See: https://github.com/divilian/PropKB
'''

import sys
import logging
import re
from copy import deepcopy
from PropKB import Literal, Clause, KB

class Node():
    def __init__(self, left=None, me=None, right=None):
        self.left = left
        self.me = me
        self.right = right
    def __repr__(self):
        retval = "Node("
        if self.left:
            retval += self.left.__repr__() + ","
        retval += self.me.__repr__()
        if self.right:
            retval += "," + self.right.__repr__()
        return retval + ")"
    def __str__(self):
        if self.left:
            return "(" + str(self.left) + self.me + str(self.right) + ")"
        else:
            return "(" + self.me + str(self.right) + ")"
    def evalu(self, assignments):
        """
        Return the result of evaluating this parse tree with the set of
        variable assignments passed. The answer should be True or False. If
        not all the variables are present in the dictionary passed,
        unpredictable behavior will result.
        """
        if not self.left:
            # The only way to not have a left child is if we're a neg
            assert self.me == "-"
            if type(self.right) is Node:
                right = self.right.evalu(assignments)
            elif type(self.right) is str:
                right = assignments[self.right]
            return not right
        else:
            if type(self.left) is Node:
                left = self.left.evalu(assignments)
            elif type(self.left) is str:
                left = assignments[self.left]
            if type(self.right) is Node:
                right = self.right.evalu(assignments)
            elif type(self.right) is str:
                right = assignments[self.right]
            if self.me == '-':
                return not right
            if self.me == '^':
                return left and right
            elif self.me == '+':
                return left or right
            elif self.me == '⊕':
                return left != right
            elif self.me == '=>':
                return not left or right
            elif self.me == '<=>':
                return left == right
            else:
                raise Exception(f"No such op {self.me}!")
    def __eq__(self, other):
        if type(other) is not Node:
            return False
        return (((self.left == None and other.left == None) or
                                            self.left == other.left)  and
            self.me == other.me  and
            self.right == other.right)

def is_in_cnf(tree):
    """
    Given a parse tree (root Node) representing a sentence in propositional
    logic, return True only if it's in CNF.
    """
    if not tree or type(tree) is str:
        # Bottomed out in an atom.
        return True
    if tree.me == "-" and type(tree.right) is str:
        return True
    if tree.me == "^":
        return is_in_cnf(tree.left) and is_in_cnf(tree.right)
    if tree.me == "+":
        return contains_only_ors(tree.left) and contains_only_ors(tree.right)
    return False

def contains_only_ors(tree):
    """
    Given a parse tree (root Node) representing a sentence in propositional
    logic, return True if it has only ors (and nots from literals).
    """
    if type(tree) is str:
        # Bottomed out in an atom.
        return True
    if tree.me == "-" and type(tree.right) is str:
        return True
    if tree.me == "+":
        return contains_only_ors(tree.left) and contains_only_ors(tree.right)
    return False


def convert_to_cnf(s):
    """
    Given a sentence (string) of propositional logic, return a set of Clause
    objects representing its equivalent in CNF.
    """
    tokens = tokenize(s)
    tree = parse(tokens)
    tree = eliminate_equiv(tree)
    tree = eliminate_implies(tree)
    tree = eliminate_xors(tree)

    # Continue to move negatives inward until we can't anymore.
    new_tree = move_neg_in(tree)
    while new_tree != tree:
        tree = new_tree
        new_tree = move_neg_in(tree)

    # Continue to apply the distributive law until we can't anymore.
    new_tree = distribute(tree)
    while new_tree != tree:
        tree = new_tree
        new_tree = distribute(tree)

    return extract_clauses(tree)


def extract_clauses(tree):
    if type(tree) is str:
        return {Clause.parse(tree)}
    clauses = set()
    if tree.me == '^':
        clauses |= extract_clauses(tree.left)
        clauses |= extract_clauses(tree.right)
    elif tree.me in ['-','+']:
        as_text = re.sub(r'[\(\)]','', str(tree))
        as_text = re.sub(r'\+',' ', as_text)
        clauses |= {Clause.parse(as_text)}
    else:
        raise(f"Illegal operator {tree.me} in CNF sentence!")
    return clauses




def eliminate_equiv(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "<=>":
            reverse = deepcopy(non_cnf_tree)
            tree.me = "=>"
            reverse.me = "=>"
            reverse.left, reverse.right = \
                eliminate_equiv(reverse.right), eliminate_equiv(reverse.left)
            bob = Node(left=tree, me="^", right=reverse)
            return bob
        else:
            tree.left = eliminate_equiv(tree.left)
            tree.right = eliminate_equiv(tree.right)
            return tree
    else:
        return non_cnf_tree

def eliminate_xors(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "⊕":
            other = deepcopy(non_cnf_tree)
            tree.left = Node(None,"-",eliminate_xors(tree.left))
            tree.me = "^"
            tree.right = eliminate_xors(tree.right)
            other.left = eliminate_xors(other.left)
            other.me = "^"
            other.right = Node(None,"-",eliminate_xors(other.right))
            return Node(left=tree, me="+", right=other)
        else:
            tree.left = eliminate_xors(tree.left)
            tree.right = eliminate_xors(tree.right)
            return tree
    else:
        return non_cnf_tree

def eliminate_implies(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "=>":
            tree.left = Node(None,"-",eliminate_implies(tree.left))
            tree.me = "+"
            tree.right = eliminate_implies(tree.right)
            return tree
        else:
            tree.left = eliminate_implies(tree.left)
            tree.right = eliminate_implies(tree.right)
            return tree
    else:
        return non_cnf_tree

def move_neg_in(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "-":
            if type(tree.right) is Node  and  tree.right.me == "-":
                # Eliminate double-negation.
                return move_neg_in(tree.right.right)
            elif type(tree.right) is Node  and  tree.right.me == "^":
                # Turn ¬(α∧β) into (¬α∨¬β) (DeMorgan's)
                tree.right.left = Node(None,"-",move_neg_in(tree.right.left))
                tree.right.right = Node(None,"-",move_neg_in(tree.right.right))
                tree.right.me = "+"
                return tree.right
            elif type(tree.right) is Node  and  tree.right.me == "+":
                # Turn ¬(α∨β) into (¬α∧¬β) (DeMorgan's)
                tree.right.left = Node(None,"-",move_neg_in(tree.right.left))
                tree.right.right = Node(None,"-",move_neg_in(tree.right.right))
                tree.right.me = "^"
                return tree.right
            tree.left = move_neg_in(tree.left)
            tree.right = move_neg_in(tree.right)
            return tree
        else:
            tree.left = move_neg_in(tree.left)
            tree.right = move_neg_in(tree.right)
            return tree
    else:
        return non_cnf_tree

def distribute(non_cnf_tree):
    if is_in_cnf(non_cnf_tree):
        return non_cnf_tree
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == '+':
            if type(tree.left) is Node and tree.left.me == '^':
                # Here we have (α∧β)∨γ and need to get (α∨γ)∧(β∨γ).
                alpha = distribute(tree.left.left)
                beta = distribute(tree.left.right)
                gamma = distribute(tree.right)
                gamma_clone = deepcopy(gamma)
                tree.me = "^"
                tree.left = Node(alpha,"+",gamma)
                tree.right = Node(beta,"+",gamma)
                return distribute(tree)
            elif type(tree.right) is Node and tree.right.me == '^':
                # Here we have γ∨(α∧β) and need to get (γ∨α)∧(γ∨β).
                alpha = distribute(tree.right.left)
                beta = distribute(tree.right.right)
                gamma = distribute(tree.left)
                gamma_clone = deepcopy(gamma)
                tree.me = "^"
                tree.left = Node(gamma,"+",alpha)
                tree.right = Node(gamma,"+",beta)
                return distribute(tree)
            tree.left = distribute(tree.left)
            tree.right = distribute(tree.right)
            return tree
        else:
            tree.left = distribute(tree.left)
            tree.right = distribute(tree.right)
            return tree
    else:
        return non_cnf_tree

def make_node(operators, operands):
    right = operands.pop()
    if operators[-1] == '-':
        left = None
    else:
        left = operands.pop()
    operands.append(Node(left,operators.pop(),right))

def parse(tokens):
    operands = []
    ops = []
    while tokens:
        token = tokens.pop(0)
        if token in ['<=>','⇔']:
            while ops and ops[-1] not in ['(','[']:
                make_node(ops, operands)
            ops.append('<=>')
        elif token in ['=>','⇒']:
            while ops and ops[-1] not in ['(','[','<=>']:
                make_node(ops, operands)
            ops.append('=>')
        elif token in ['+','∨']:
            while ops and ops[-1] not in ['(','[','<=>','=>']:
                make_node(ops, operands)
            ops.append('+')
        elif token in ['⊕']:
            while ops and ops[-1] not in ['(','[','<=>','=>']:
                make_node(ops, operands)
            ops.append('⊕')
        elif token in ['^','∧']:
            while ops and ops[-1] not in ['(','[','<=>','=>','+']:
                make_node(ops, operands)
            ops.append('^')
        elif token in ['-','¬']:
            while ops and ops[-1] not in ['(','[','<=>','=>','+','^','∧']:
                make_node(ops, operands)
            ops.append('-')
        elif token in ['(','[']:
            ops.append(token)
        elif token in [')']:
            while ops and ops[-1] not in ['(']:
                make_node(ops, operands)
            ops.pop()
        elif token in [']']:
            while ops and ops[-1] not in ['[']:
                make_node(ops, operands)
            ops.pop()
        else:
            operands.append(token)

    # No more input tokens. Finish up everything left undone.
    while ops:
        make_node(ops, operands)

    return operands.pop()

def tokenize(s):
    """
    Given a sentence (string) of propositional logic, return a list of its
    tokens. Each token is a banana, a prop logic connective, or a symbol
    (string). Legal syntax includes:
        - () and [] for grouping
        - - or ¬ for "not"
        - ^ or ∧ for "and"
        - + or ∨ for "or"
        - => or ⇒ for "implies"
        - <=> or ⇔ for "equiv"
        - ⊕ for "xor"
    """
    return re.findall(r'\(|\)|\[|\]|\^|\+|=>|<=>|-|¬|⇒|⇔|∧|∨|⊕|\w+', s)


if __name__ == "__main__":

    # This main program will read Propositional Logic (not CNF) from a file,
    # then both (1) parse it to a tree and (2) create a KB from it, which
    # will convert it to a set of CNF clauses. It will then verify the two
    # are equivalent by exhaustively testing every possible set of variable
    # assignments.

    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) != 2:
        sys.exit("Usage: cnf.py filename.kb.")

    filename = sys.argv[1]
    print(f"Converting from {filename}...")

    with open(filename, encoding="utf-8") as f:
        sentence = " ^ ".join([ "(" + l + ")" for l in f.readlines() ])
        sentence = re.sub(r'\n','',sentence)
    non_cnf = parse(tokenize(sentence))
    in_cnf = KB(filename)
    if in_cnf.is_equiv(non_cnf):
        print(f"Confirmed: CNF version and original version are equivalent.")
    else:
        print(f"Whoops: CNF version and original version differ!")
