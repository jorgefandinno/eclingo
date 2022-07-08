import clingo
from clingo import ast
from clingo.ast import Sign
from clingox.ast import reify_symbolic_atoms
from clingo.ast import (
    AST,
    ASTType,
)

#print(x.atom.symbol.arguments[0]) # Will give me the arguments to construct the args
#print(x.sign) # will give me what kind of sign 
def symbolic_literal_to_term(x: AST) -> AST:
    assert x.ast_type == ASTType.Literal and x.atom.ast_type == ASTType.SymbolicAtom
    symbol = x.atom.symbol

    # Create List of arguments 
    arg_list = []
    for i in range(len(symbol.arguments)):
        arg_list.append((symbol.arguments[i]))
        
    name = refine_name(x.sign, x.atom)

    return ast.Function(x.location, name, arg_list, False)

def refine_name(sign, stm) -> str:
    if (sign == Sign.Negation):
        name = 'not1'
        return str(reify_symbolic_atoms(stm, name, reify_strong_negation=True))
    elif (sign == Sign.DoubleNegation):
        name = 'not2'
        return str(reify_symbolic_atoms(stm, name, reify_strong_negation=True))
    return stm.symbol.name