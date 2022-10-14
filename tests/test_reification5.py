#  u(a) :- u(b), k(c) | --output=reify
# echo "a :- b. k{b}." | clingo --output=reify  

import unittest
from typing import cast
from clingo import ast
from clingox.pprint import pprint
from clingox.testing.ast import ASTTestCase, parse_statement

from eclingo.config import AppConfig
from eclingo.parsing import parser
from eclingo.parsing.transformers import ast_reify, function_transformer
from tests.test_reification2 import parse_literal
from clingox.reify import reify_program

def flatten(lst):
    result = []
    for lst2 in lst:
        if isinstance(lst2, list):
            for e in lst2:
                result.append(e)
        else:
            result.append(lst2)

    return result

def parse_program(stm, parameters=[], name="base"):
    ret = []
    parser.parse_program(
        stm,
        ret.append,
        parameters,
        name,
        config=AppConfig(semantics="c19-1", verbose=0, use_reification=True),
    )
    return flatten(ret)

def clingo_parse_program(stm):
    ret = []
    ast.parse_string(stm, ret.append)
    ret = [rule for rule in ret]
    return ret

class TestCase(ASTTestCase):
    def setUp(self):
        self.print = False

    def assert_equal_program(self, program, expected):
    
        # Split and strip whitespaces on '.' based on string given
        expected_program = [x.strip() for x in expected.split('.') if x]
        reified_program = [str(sym) for sym in program]
        
        # Delete tag
        del reified_program[0]
    
        print("The reified program:\n", reified_program)
        print("The expected program:\n", expected_program)
        
        
        
        if len(reified_program) != len(expected_program):
            self.fail(
                f"Lists differ (different lenghts {len(reified_program)} and {len(expected_program)}"
            )
        for e1, e2 in zip(reified_program, expected_program):
            self.assertEqual(e1, e2)
        self.assertListEqual(reified_program, expected_program)

class Test(TestCase):
    def test_epistemic_rules(self):
        self.assert_equal_program(
            reify_program("a :- b. k{b}."), "atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)). atom_tuple(1). literal_tuple(1). literal_tuple(1,1). rule(disjunction(1),normal(1))."
        )