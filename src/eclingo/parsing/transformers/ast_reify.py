import clingo
from clingo import ast
from clingo.ast import (
    AST,
    ASTType,
)

def symbolic_literal_to_term(x: AST) -> AST:
    assert x.ast_type == ASTType.Literal and x.atom.ast_type == ASTType.SymbolicAtom
    arg = ast.SymbolicTerm(x.location, clingo.Function(x.name, [], True))
    return ast.Function(x.location, x.name, [arg], False)