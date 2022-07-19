import clingox
from clingox.ast import theory_term_to_term
from clingo.ast import AST

from eclingo.parsing.transformers import ast_reify
from .ast_tester import ASTTestCase
from tests.test_reification2 import parse_literal, parse_term


class Test(ASTTestCase):
    
    def test_theory_atom(self):  
        self.assertEqual(
            ast_reify.theory_atom_to_function(parse_literal("&k{ p(X) }")),
            parse_term("k(p(X))")
        )
        
        self.assertEqual(
            ast_reify.theory_atom_to_function(parse_literal("&k{ a(Y) }")),
            parse_term("k(a(Y))")
        )
        
        self.assertEqual(
            ast_reify.theory_atom_to_function(parse_literal("&k{ b(c) }")),
            parse_term("k(b(c))")
        )
        