# To be merged with test_reification.py later
# Let us keep it as a separated file until finishing with the current patch

from .ast_tester import ASTTestCase
from typing import cast
from clingo import ast
from clingo.ast import AST
from eclingo.parsing.transformers import ast_reify

def last_stm(s: str) -> AST:
    """
    Convert string to rule.
    """
    stm = None

    def set_stm(x):
        nonlocal stm
        stm = x

    ast.parse_string(s, set_stm)

    return cast(AST, stm)

def parse_literal(s: str) -> AST:
    stm = last_stm(f":-{s}.")
    return stm.body[0]

def parse_term(s: str) -> AST:
    lit = parse_literal(f"p({s})")
    return lit.atom.symbol.arguments[0]

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

class Test(ASTTestCase):

    def assert_symbolic_literal_to_term(self, lit: str, term: str):
        parsed_lit = parse_literal(lit)
        parsed_term = parse_term(term)
        result = ast_reify.symbolic_literal_to_term(parsed_lit)
        self.maxDiff = None
        self.assertEqual(result, parsed_term)

    def test_symbolic_literal_to_term(self):
        #self.assert_symbolic_literal_to_term("-a(b,c)","-a(b,c)")
        
        self.assert_symbolic_literal_to_term("a(b)","a(b)")
        self.assert_symbolic_literal_to_term("a","a")
        self.assert_symbolic_literal_to_term("not a","not1(a)")
        self.assert_symbolic_literal_to_term("not not a","not2(a)")
        
        self.assert_symbolic_literal_to_term("a(b,c)","a(b,c)")
        self.assert_symbolic_literal_to_term("not a(b,c)","not1(a(b,c))")
        self.assert_symbolic_literal_to_term("not not a(b,c)","not2(a(b,c))")
        '''
        self.assert_symbolic_literal_to_term("not -a(b,c)","not1(-a(b,c))")
        self.assert_symbolic_literal_to_term("not not -a(b,c)","not2(-a(b,c))")
        '''

