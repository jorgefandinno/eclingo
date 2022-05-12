from typing import List
from clingo import ast as _ast

# pylint: disable=all

# def atom(location: dict, positive: bool, name: str, arguments: List) -> _ast.AST:
def atom(location: _ast.Location, positive: bool, name: str, arguments: List) -> _ast.AST:

    """
    Helper function to create an atom.

    Arguments:
    location --  Location to use.
    positive --  Classical sign of the atom.
    name     --  The name of the atom.
    arguments -- The arguments of the atom.
    """
    ret = _ast.Function(location, name, arguments, False)
    if not positive:
        ret = _ast.UnaryOperation(location, _ast.UnaryOperator.Minus, ret)
    return _ast.SymbolicAtom(ret)




