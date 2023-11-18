'''
CPSC 415 -- Homework support file
Stephen Davies, University of Mary Washington, fall 2023
See: https://github.com/divilian/PropKB
'''

import sys
import os
import re
from copy import copy, deepcopy
import numpy as np
import logging
from itertools import product

class Literal():
    def __init__(self, varstring):
        if varstring[0] == "-":
            self.neg = True
            self.var = varstring[1:]
        else:
            self.neg = False
            self.var = varstring
    def negated_form_of(self):
        a_copy = copy(self)
        a_copy.neg = not self.neg
        return a_copy
    def __str__(self):
        if self.neg:
            return "¬" + str(self.var)
        else:
            return str(self.var)
    def __repr__(self):
        return f"Literal({'¬' if self.neg else ''}{self.var})"
    def __hash__(self):
        return self.var.__hash__()
    def __eq__(self, other):
        return self.var == other.var  and  self.neg == other.neg

class Clause():
    def __init__(self):
        self.lits = set()
    @classmethod
    def parse(cls, string):
        retval = cls()
        splits = [ s for s in re.split(r'\s+',string) if len(s) > 0 ]
        retval.lits = { Literal(v) for v in splits }
        return retval
    def add_literal(self, lit):
        self.lits.add(lit)
    def remove_literal(self, lit):
        self.lits.remove(lit)
    def is_unit(self):
        return len(self.lits) == 1
    def contains_literal(self, lit):
        return lit in self.lits
    def contains_variable(self, var):
        return var in [ l.var for l in self.lits ]
    def polarity_of_variable(self, var):
        for lit in self.lits:
            if lit.var == var:
                return lit.neg
    def evalu(self, assignments):
        """
        Given a dict of variables to values, return True if this clause is True
        under that assignment.
        """
        return any([assignments[lit.var] != lit.neg for lit in self.lits ])
    # Not overriding __eq__() as this causes cascading infinite loops.
    def equivalent_to(self, other):
        return (all([ sl in other.lits for sl in self.lits ]) and
            all([ ol in self.lits for ol in other.lits ]))
    def __str__(self):
        return " ∨ ".join(str(l) for l in list(self.lits))
    def __repr__(self):
        return f"Clause({self.lits})"

class KB():
    """
    A propositional logic knowledge base, with .tell() and .ask() methods
    supporting arbitrary PL sentences.
    """
    def __init__(self, filename=None):
        from cnf import convert_to_cnf
        self.vars = set()
        self.clauses = set()
        if filename:
            already_in_cnf = filename.endswith('.cnf')
            # If the file whose name is passed is known to already be in CNF,
            # we can skip a step and just create Clauses directly.
            with open(filename, "r", encoding="utf-8") as f:
                for clause_line in [ l.strip() for l in f.readlines() ]:
                    if not clause_line.startswith("#"):
                        if not already_in_cnf:
                            clauses = convert_to_cnf(clause_line)
                            for clause in clauses:
                                self.add_clause(clause)
                        else:
                            self.add_clause(Clause.parse(clause_line))
            for c in self.clauses:
                self.vars |= { l.var for l in c.lits }

    def tell(self, fact):
        """
        Update this KB by adding the passed fact (represented as a string of
        propositional logic).
        """
        from cnf import convert_to_cnf
        for clause in convert_to_cnf(fact):
            self.add_clause(clause)

    def retract(self, fake_news):
        """
        Update this KB by removing the passed non-fact (represented as a string
        of propositional logic) if it was entered earlier. This isn't as easy
        as it sounds, and won't always work if the exact negation of the fake
        news wasn't directly previously inserted, but rather was derived from
        previous facts.
        """
        from cnf import convert_to_cnf
        clauses_to_remove = set()
        for retracted_clause in convert_to_cnf(fake_news):
            for clause in self.clauses:
                if retracted_clause.equivalent_to(clause):
                    clauses_to_remove |= {clause}
        for clause in clauses_to_remove:
            self.remove_clause(clause)

    def ask(self, hypothesis):
        """
        Given a string of propositional logic, return whether this KB can
        confirm it is True, can confirm it is False, or cannot confirm either
        way (the value in the latter case will be the string "IDK").
        """
        if self.can_prove(hypothesis):
            return True
        elif self.can_prove("-(" + hypothesis + ")"):
            return False
        return "IDK"

    def get_solution(self):
        """
        If possible, return a sample solution (set of assignments to variables)
        that satisfies this knowledge base. Otherwise, return False.
        """
        remaining_clauses = deepcopy(self.clauses)
        assignments = {}
        return self.solve_rec(remaining_clauses, assignments)

    def is_equiv(self, other):
        """
        Exhaustively try every set of assignments to variables and return True
        only if this KB has all the same answers as the other object passed,
        which might be another KB, or might be a parse tree (Node) from the
        cnf package. Warning: this is exponential in the number of variables,
        of course.
        """
        if type(other) is KB  and  self.vars != other.vars:
            # C'mon, don't waste my time.
            return False
        ret_val = {}
        the_vars = list(self.vars)
        some_vals = product({True,False},repeat=len(the_vars))
        for some_val in some_vals:
            assignments = { k:v for k,v in zip(the_vars, some_val) }
            if self.evalu(assignments) != other.evalu(assignments):
                return False
        return True

    def audit(self):
        """
        Return a dict whose keys are the variables of this KB, and whose
        values are either True, False, or "IDK" (don't know).
        """
        ret_val = {}
        for var in self.vars:
            if self.can_prove(var):
                ret_val[var] = True
            elif self.can_prove("-" + var):
                ret_val[var] = False
            else:
                ret_val[var] = "IDK"
        return ret_val

    def can_prove(self, hypothesis):
        """
        Return True if the hypothesis passed (a string of prop logic) is
        guaranteed to be true by this knowledge base, and False otherwise.
        """
        from cnf import convert_to_cnf
        neg_hypo_clauses = convert_to_cnf("-(" + hypothesis + ")")
        remaining_clauses = deepcopy(self.clauses)
        remaining_clauses |= neg_hypo_clauses
        assignments = {}
        if self.solve_rec(remaining_clauses, assignments):
            return False
        else:
            return True

    def add_clause(self, clause):
        self.clauses |= {clause}
        self.vars |= { l.var for l in clause.lits }

    def remove_clause(self, clause):
        self.clauses -= {clause}

    def evalu(self, assignments):
        """
        Given a dict of variables to values, return True if this KB is True
        under that assignment.
        """
        return all([ c.evalu(assignments) for c in self.clauses ])

    def propagate_units(self, remaining_clauses, assignments):
        """
        For all "unit clauses" (only one literal) perform the obvious
        simplifications: auto-satisfy any clauses that match it, and remove
        its negation from any clauses that match its negation.
        """
        while remaining_clauses:
            nrc = len(remaining_clauses)
            i = 0
            while i < nrc and not list(remaining_clauses)[i].is_unit():
                i += 1
            if i == nrc:
                break
            else:
                unit_clause = list(remaining_clauses)[i]
                the_lit = list(unit_clause.lits)[0]
                if the_lit.var in assignments:
                    if the_lit.neg != (not assignments[the_lit.var]):
                        # Houston, we have a problem. We have at least two unit
                        # clauses with opposite polarity!
                        sys.exit(f"Inherently incompatible {the_lit.var}.")
                assignments[the_lit.var] = not the_lit.neg
                remaining_clauses -= {unit_clause}

                # For every unit clause, we know that the value of its only
                # literal is trivially set in stone. So, if there's any other
                # clause that also has that literal, we can just get rid of it
                # since it's already satisfied.
                clauses_to_remove = []
                for c in remaining_clauses:
                    if c.contains_literal(the_lit):
                        clauses_to_remove += [c]
                for ctr in clauses_to_remove:
                    remaining_clauses -= {ctr}

                # On the other hand, we also know that the negation of this
                # literal will *never* be true. So, remove that negation in any
                # other clause in which it occurs. If that gives an empty
                # clause, we're doomed.
                for c in remaining_clauses:
                    negated_form = the_lit.negated_form_of()
                    if c.contains_literal(negated_form):
                        c.remove_literal(negated_form)
            continue

    #def elim_easy_doubles: TODO if the same literal appears twice in a clause
    # with the same polarity, remove all but one for convenience. If it appears
    # with *both* polarities, then the clause is trivially true.

    def pure_elim(self, remaining_clauses, assignments):
        """
        For any variable that appears with only one polarity, go ahead and set
        it to what it needs to be.
        """
        made_progress = False
        for vn in self.vars:
            cs = [ c for c in remaining_clauses if c.contains_variable(vn) ]
            pols = { c.polarity_of_variable(vn) for c in cs }
            if len(pols) == 0:
                # Must have been removed by propagate_units(). Never mind.
                pass
            if len(pols) == 1:
                # Great! It's pure. Eliminate it.
                if list(pols)[0] == 1:
                    assignments[vn] = True
                else:
                    assignments[vn] = False
                for c in cs:
                    remaining_clauses -= {c}
                made_progress = True
        return made_progress

    def solve_rec(self, remaining_clauses, assignments):
        self.propagate_units(remaining_clauses, assignments)
        # As long as we're making progress, keep pure_elim'ing.
        while self.pure_elim(remaining_clauses, assignments):
            pass
        if any([ len(c.lits) == 0 for c in remaining_clauses ]):
            # This is a contradiction! Return False.
            return False
        remaining_vars = self.vars - set(assignments.keys())
        if len(remaining_vars) == 0:
            return assignments
        var_to_try = list(remaining_vars)[0]
        assignments_try_true = deepcopy(assignments)
        assignments_try_true[var_to_try] = True
        result = self.solve_rec(remaining_clauses, assignments_try_true)
        if result:
            return result
        assignments_try_false = deepcopy(assignments)
        assignments_try_true[var_to_try] = False
        result = self.solve_rec(remaining_clauses, assignments_try_true)
        if result:
            return result
        return False


    def __str__(self):
        return " ∧ ".join(f"({c})" for c in list(self.clauses))
    def __repr__(self):
        return f"KB({self.clauses})"


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) not in [1,2]:
        sys.exit("Usage: PropKB [prop_logic_file.kb|cnf_file.cnf].")

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            sys.exit(f"No such file {filename}.")
        myKB = KB(sys.argv[1])
        print(f"Loaded {filename}.")
    else:
        myKB = KB()
        print("Created empty KB.")

    print("Add (additional) facts to the KB like this 'tell: (b ^ c) => d'")
    print("Query the KB like this 'ask: a + -b'")
    pattern = re.compile(r'(?P<cmd>\w+):? ?(?P<sent>.*)')
    user_input = input("ask/tell/vars (done): ")
    while user_input != "done":
        matches = pattern.match(user_input)
        if matches:
            if matches['cmd'][0] in ['A','a']:
                print(myKB.ask(matches['sent']))
            elif matches['cmd'][0] in ['T','t']:
                myKB.tell(matches['sent'])
                print("Updated KB.")
            elif matches['cmd'][0] in ['V','v']:
                print(f"Vars: {','.join(sorted(myKB.vars))}")
            else:
                print(f"Didn't understand command '{user_input}'.")
        else:
            print(f"Didn't understand command '{user_input}'.")
        user_input = input("ask/tell/vars (done): ")
