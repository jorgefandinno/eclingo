from typing import List

import clingo
from clingo import ast
from clingo.ast import AST, ASTType, Sign

"""
    Reify function. Gets an AST of a literal and parses it to obtain an ASTType.Function
    Cases where:
        1. Negation or DoubleNegation (Based on sign)
        2. Basic Symbolic Term, returns ASTType.SymbolicTerm
        3. No negation
        4. Unary Operation of explicit negation
"""


def symbolic_literal_to_term(x: AST) -> AST:
    symbol = x.atom.symbol
    sign_name = refine_name(x.sign)

    args: List[AST] = []
    if x.atom.symbol.ast_type == ASTType.UnaryOperation:
        return unary_parsing(x, sign_name, args)

    len_list = len(symbol.arguments)

    if sign_name == "not1" or sign_name == "not2":  # Base Case -> Negation
        if not len_list:
            # Base Case 1. No Symbolic term arguments, then literal becomes only argument to not1/2 negation.
            lit_fun = [
                ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))
            ]

        else:
            args = argument_parser(x, symbol.arguments)
            lit_fun = [ast.Function(x.location, symbol.name, args, False)]

    elif len_list < 1:
        # No arguments and no negation case -> Return basic Symbolic Term
        return ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))

    else:
        lit_fun = argument_parser(x, symbol.arguments)
        sign_name = symbol.name

    return ast.Function(x.location, sign_name, lit_fun, False)


"""
    Helper Function: 
    Parses term for ASTType Unary Operation.
"""


def unary_parsing(x: AST, sign_name: str, args: List[AST]):
    symbol = x.atom.symbol
    symbol = symbol.argument

    n = len(symbol.arguments)
    if n < 1:
        n_arg = ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))
        return ast.UnaryOperation(x.location, 0, n_arg)

    args = argument_parser(x, symbol.arguments)
    lit_fun = ast.Function(x.location, symbol.name, args, False)
    unary_term = ast.UnaryOperation(x.location, 0, lit_fun)

    if sign_name == "not1" or sign_name == "not2":
        return ast.Function(x.location, sign_name, [unary_term], False)

    return unary_term


"""
    Helper Function: Refines Negation names based on sign of AST
"""


def refine_name(sign: Sign) -> str:
    name = ""
    if sign == Sign.Negation:
        name = "not1"
    elif sign == Sign.DoubleNegation:
        name = "not2"
    return name


"""
    Helper function:
    Parses a literal for which there are SymbolicTerms or Variables as arguments
"""

def argument_parser(x: AST, arguments: list) -> List[AST]:
    arg_list: List[AST] = []
    n = len(arguments)
    for t in range(n):
        if arguments[t].ast_type == ASTType.Function:
            funct_arg = argument_parser(x, arguments[t].arguments)
            arg = ast.Function(x.location, arguments[t].name, funct_arg, False)

        elif arguments[t].ast_type == ASTType.Variable:
            arg = ast.Variable(x.location, str(arguments[t]))

        else:
            arg = ast.SymbolicTerm(
                x.location, clingo.Function(str(arguments[t]), [], True)
            )
        arg_list.append(arg)

    return arg_list
