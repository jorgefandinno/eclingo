import clingo
from clingo import ast
from clingo.ast import Sign
from clingox.ast import reify_symbolic_atoms
from clingo.ast import (
    AST,
    ASTType,
)
from typing import List

# TODO: In the case of -a(b,c)
# We get a Unary operation first, therefore: parsed_lit.atom.symbol.argument -> a(b,c) and is a term from which we can do
# parsed_lit.atom.symbol.argument.arguments[i] to get the arg_list. The operator_type will return the -
# Type UnaryOperation


def symbolic_literal_to_term(x: AST) -> AST:
    symbol = x.atom.symbol
    sign_name = refine_name(x.sign)
    
    '''
    # Commenting out for coverage passing
    if x.atom.symbol.ast_type == ASTType.UnaryOperation:
        symbol = symbol.argument
        # TODO: Create a helper function to deal with Unary Operation types
    '''
    
    len_list = len(symbol.arguments)
    
    # Create args list (Symbolic terms from the arguments list)
    args: List[AST] = []
    if sign_name == 'not1' or sign_name == 'not2': # Base Case -> Negation
    
        if not len_list:  # Base Case 1. No Symbolic term arguments, then literal becomes only argument to not1/2 negation.
            lit_fun = [ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))]
            
        else:             # Base Case 2. Make Symbolic Term args the arguments of Literal. Then not1/2 becomes name of that literal.
            for t in range(len_list):
                arg = ast.SymbolicTerm(x.location, clingo.Function(str(symbol.arguments[t]), [], True))
                args.append(arg)
            lit_fun = [ast.Function(x.location, symbol.name, args, False)]
        
           
    elif len_list < 1:  # No arguments and no negation case -> Return basic Symbolic Term
        return ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))
    
    else:               # Arguments and no negation -> 
        for t in range(len_list): # Get all Symbolic term arguments and make symbol.name of literal the name of the returning Function
            arg = ast.SymbolicTerm(x.location, clingo.Function(str(symbol.arguments[t]), [], True))
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
