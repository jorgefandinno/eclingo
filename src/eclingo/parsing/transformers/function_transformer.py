"""Module providing an AST function Trasnformer"""
import clingo
from clingo import ast
from clingo.ast import Transformer


def rule_to_symbolic_term_adapter(rules):
    """Helper function"""
    rule_trans = SymbolicTermToFunctionTransformer()
    rule = rule_trans.visit_sequence(rules)
    return rule


class SymbolicTermToFunctionTransformer(Transformer):
    """Transforms a SymbolicTerm AST into a Function AST"""

    def visit_SymbolicTerm(self, term):  # pylint: disable=invalid-name
        """Visit AST to find SymbolicTerm"""

        if term.symbol.type != clingo.SymbolType.Function:
            return term

        location = term.location
        symbol = term.symbol
        name = symbol.name
        arguments = symbol.arguments

        function = ast.Function(location, name, arguments, False)
        return function
