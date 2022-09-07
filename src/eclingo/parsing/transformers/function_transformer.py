from typing import Iterable, List, Set, Tuple, Union, cast

from clingo import ast
from clingo.ast import AST, Transformer


def _rule_to_symbolic_term_adapter(rules):
    rule_trans = SymbolicTermToFunctionTransformer()
    rule = rule_trans.visit_sequence(rules)
    return rule


class SymbolicTermToFunctionTransformer(Transformer):
    def visit_SymbolicTerm(self, term):
        location = term.location
        symbol = term.symbol
        name = symbol.name
        arguments = symbol.arguments

        # Create Function from SymbolicTerm
        function = ast.Function(location, name, arguments, False)
        return function
