"""
This module contains functions for reififcation of `AST` objects
"""
import clingo
from clingo import ast
from clingo.ast import AST, ASTType, Sign


def _positive_symbolic_literal_to_term(x: AST):
    """
    Helper function to ensure proper treatment of clingo.Function and ast.Function
    """
    if x.ast_type != ast.ASTType.Function or x.arguments or x.external:
        return x
    return ast.SymbolicTerm(x.location, clingo.Function(x.name, [], True))


def symbolic_literal_to_term(
    lit: AST, negation_name: str = "not1", double_negation_name: str = "not2"
) -> AST:
    """
    Convert the given literal into a clingo term according to the following rules:
    - `atom => atom`
    - `not atom => not1(atom)`
    - `not not atom => not2(atom)`

    Parameters
    ----------
    lit
        An `AST` that represents a literal.
    negation_name
        A string to be used to represent negation.
    double_negation_name
        A string to be used to represent double negation.

    Returns
    -------
    An `AST` that represnts the reified literal as a term.
    """
    assert lit.ast_type == ASTType.Literal
    if lit.atom.ast_type != ASTType.SymbolicAtom:
        return lit
    symbol = lit.atom.symbol

    if lit.atom.symbol.ast_type == ASTType.UnaryOperation:
        symbol = symbol.argument

    symbol = _positive_symbolic_literal_to_term(symbol)

    if lit.atom.symbol.ast_type == ASTType.UnaryOperation:
        symbol = ast.UnaryOperation(lit.location, 0, symbol)

    if lit.sign == ast.Sign.NoSign:
        return symbol

    sign_name = negation_name if lit.sign == Sign.Negation else double_negation_name

    return ast.Function(lit.location, sign_name, [symbol], False)
