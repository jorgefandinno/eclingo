import clingo
from clingo import ast
from clingo.ast import Sign
from clingox.ast import reify_symbolic_atoms
from clingo.ast import (
    AST,
    ASTType,
)
from typing import List

def symbolic_literal_to_term(x: AST) -> AST:
    symbol = x.atom.symbol
    sign_name = refine_name(x.sign) # Returns not1, not2 or '' (empty str)

    # Create List of arguments 
    arg_list = []
    for i in range(len(symbol.arguments)):
        arg_list.append((symbol.arguments[i]))
    
    # Create args list (Symbolic terms from the arguments list)
    args: List[AST] = []
    if sign_name == 'not1' or sign_name == 'not2': # Base Case -> Negation
    
        for t in range(len(arg_list)): # Get all Symbolic term arguments
            arg = ast.SymbolicTerm(x.location, clingo.Function(str(arg_list[t]), [], True))
            args.append(arg)

        if not arg_list: # Base Case 1. No Symbolic term arguments, then literal becomes only argument to not1/2 negation.
            lit_fun = [ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))]
        else:            # Base Case 2. Make Symbolic Term args the arguments of Literal. Then not1/2 becomes name of that literal.
            lit_fun = [ast.Function(x.location, symbol.name, args, False)]
            
    elif not arg_list:  # No arguments and no negation case -> Return basic Symbolic Term
        return ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))
    
    else:               # Arguments and no negation -> 
        for t in range(len(arg_list)): # Get all Symbolic term arguments and make symbol.name of literal the name of the returning Function
            arg = ast.SymbolicTerm(x.location, clingo.Function(str(arg_list[t]), [], True))
            args.append(arg)
        lit_fun = args
        sign_name = symbol.name
        
    return ast.Function(x.location, sign_name, lit_fun, False)

# Helper Function to refine Negation names
def refine_name(sign) -> str:
    name = ''
    if (sign == Sign.Negation):
        name = 'not1'
    elif (sign == Sign.DoubleNegation):
        name = 'not2'
    return name
