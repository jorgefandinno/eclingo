from typing import List

import clingo
from clingo import ast
from clingo.ast import AST, ASTType, Sign


def function_wrapper(x: ASTType.Function, loc: AST, args: List[AST], name_f: str):
    # Recursive base case -> If Type is function keep iterating until all arguments have been processed
    type_args = x.ast_type
    new_args: List[AST] = []

    # x -> Is the whole Function. Example (b(t(X)))
    if type_args == ASTType.Function:
        for n in range(len(x.arguments)):
            funct = function_wrapper(x.arguments[n], loc, args, x.name)
            new_args.append(funct)

        if name_f == x.name:
            return funct

        final = ast.Function(loc.location, name_f, new_args, False)
        return final

    if x.ast_type == ASTType.Variable:
        arg = ast.Variable(loc.location, str(x))
    else:
        arg = ast.SymbolicTerm(loc.location, clingo.Function(str(x), [], True))
    new_args.append(arg)

    return ast.Function(loc.location, name_f, new_args, False)


def symbolic_literal_to_term(x: AST) -> AST:
    symbol = x.atom.symbol
    sign_name = refine_name(x.sign)

    args: List[AST] = []
    if x.atom.symbol.ast_type == ASTType.UnaryOperation:
        return unary_parsing(x, sign_name, args)

    len_list = len(symbol.arguments)
    # Create args list (Symbolic terms from the arguments list)
    if sign_name == "not1" or sign_name == "not2":  # Base Case -> Negation
        if not len_list:
            # Base Case 1. No Symbolic term arguments, then literal becomes only argument to not1/2 negation.
            lit_fun = [
                ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))
            ]

        else:
            # Base Case 2. Make Symbolic Term args or Variable the arguments of Literal. Then not1/2 becomes name of that literal.
            for t in range(len_list):
                if symbol.arguments[t].ast_type == ASTType.Function:
                    name_func_sym = symbol.arguments[t].name
                    arg = function_wrapper(symbol.arguments[t], x, args, name_func_sym)

                elif symbol.arguments[t].ast_type == ASTType.Variable:
                    arg = ast.Variable(x.location, str(symbol.arguments[t]))
                else:
                    arg = ast.SymbolicTerm(
                        x.location, clingo.Function(str(symbol.arguments[t]), [], True)
                    )
                args.append(arg)
            lit_fun = [ast.Function(x.location, symbol.name, args, False)]

    elif len_list < 1:
        # No arguments and no negation case -> Return basic Symbolic Term
        return ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))

    else:
        # Arguments and no negation ->
        for t in range(len_list):
            if symbol.arguments[t].ast_type == ASTType.Function:
                name_func_sym = symbol.arguments[t].name
                arg = function_wrapper(symbol.arguments[t], x, args, name_func_sym)

            elif symbol.arguments[t].ast_type == ASTType.Variable:
                arg = ast.Variable(x.location, str(symbol.arguments[t]))

            else:
                # Get all Symbolic term arguments and make symbol.name of literal the name of the returning Function
                arg = ast.SymbolicTerm(
                    x.location, clingo.Function(str(symbol.arguments[t]), [], True)
                )

            args.append(arg)

        lit_fun = args
        sign_name = symbol.name

    return ast.Function(x.location, sign_name, lit_fun, False)


def unary_parsing(x: AST, sign_name: str, args: List[AST]):
    symbol = x.atom.symbol
    symbol = symbol.argument

    n = len(symbol.arguments)
    if n < 1:
        n_arg = ast.SymbolicTerm(x.location, clingo.Function(symbol.name, [], True))
        return ast.UnaryOperation(x.location, 0, n_arg)

    for t in range(n):
        if symbol.arguments[t].ast_type == ASTType.Function:
            name_func_sym = symbol.arguments[t].name
            arg = function_wrapper(symbol.arguments[t], x, args, name_func_sym)

        elif symbol.arguments[t].ast_type == ASTType.Variable:
            arg = ast.Variable(x.location, str(symbol.arguments[t]))

        else:
            arg = ast.SymbolicTerm(
                x.location, clingo.Function(str(symbol.arguments[t]), [], True)
            )
        args.append(arg)
    lit_fun = ast.Function(x.location, symbol.name, args, False)
    unary_term = ast.UnaryOperation(x.location, 0, lit_fun)

    if sign_name == "not1" or sign_name == "not2":
        return ast.Function(x.location, sign_name, [unary_term], False)

    return unary_term


# Helper Function to refine Negation names
def refine_name(sign) -> str:
    name = ""
    if sign == Sign.Negation:
        name = "not1"
    elif sign == Sign.DoubleNegation:
        name = "not2"
    return name
