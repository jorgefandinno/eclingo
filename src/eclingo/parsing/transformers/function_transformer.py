"""Module providing an AST function Trasnformer"""
import clingo
from clingo import ast
from clingo.ast import ASTType, Transformer


def _rule_to_symbolic_term_adapter(rules):
    """Helper function"""
    rule_trans = SymbolicTermToFunctionTransformer()
    rule = rule_trans.visit_sequence(rules)
    return rule


class SymbolicTermToFunctionTransformer(Transformer):
    """Transforms a SymbolicTerm AST into a Function AST"""

    def visit_Interval(self, term):  # pylint disable=invalid-name
        """Visit AST to ensure right Interval element is SymbolicTerm"""

        assert term.right.ast_type == ASTType.SymbolicTerm

        return term

    def visit_Heuristic(self, term):  # pylint disable=invalid-name
        """Visit AST to ensure modifier Heuristic element is SymbolicTerm"""

        new_args = []
        for x in term.atom.symbol.arguments:
            if x.ast_type == ASTType.SymbolicTerm:

                location = x.location
                symbol = x.symbol
                name = symbol.name
                arguments = symbol.arguments

                function = ast.Function(location, name, arguments, False)
                new_args.append(function)
        term.atom.symbol.arguments = new_args

        final_atom = ast.SymbolicAtom(term.atom.symbol)
        fin_heur = ast.Heuristic(
            term.location,
            final_atom,
            term.body,
            term.bias,
            term.priority,
            term.modifier,
        )

        return fin_heur

    def visit_SymbolicTerm(self, term):  # pylint disable=invalid-name
        """Visit AST to find SymbolicTerm"""

        if term.symbol.type != clingo.SymbolType.Function:
            return term

        location = term.location
        symbol = term.symbol
        name = symbol.name
        arguments = symbol.arguments

        function = ast.Function(location, name, arguments, False)
        return function
