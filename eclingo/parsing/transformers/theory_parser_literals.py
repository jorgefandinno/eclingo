"""
Module with functions to transform theory elements into literals.
"""
# pylint: disable=all
import clingo
from clingo import ast
from . import astutil
from clingo.ast import Transformer


class TheoryTermToTermTransformer(Transformer):
    """
    This class transforms a given theory term into a plain term.
    """
    def visit_TheoryTermSequence(self, x):
        """
        Theory term tuples are mapped to term tuples.
        """
        if x.sequence_type == ast.TheorySequenceType.Tuple:
            return ast.Function(x.location, "", [self(a) for a in x.arguments], False)
        else:
            raise RuntimeError("invalid term: {}".format(x.location))

    def visit_TheoryFunction(self, x):
        """
        Theory functions are mapped to functions.

        If the function name refers to a function in the table, an exception is thrown.
        """
        isnum = lambda y: y.type == ast.ASTType.Symbol and y.symbol.type == clingo.SymbolType.Number
        if x.name == "-" and len(x.arguments) == 1:
            rhs = self(x.arguments[0])
            if isnum(rhs):
                return ast.Symbol(x.location, clingo.Number(-rhs.symbol.number))
            else:
                return ast.UnaryOperation(x.location, ast.UnaryOperator.Minus, rhs)
        elif (x.name == "+" or x.name == "-") and len(x.arguments) == 2:
            lhs = self(x.arguments[0])
            rhs = self(x.arguments[1])
            op  = ast.BinaryOperator.Plus if x.name == "+" else ast.BinaryOperator.Minus
            if isnum(lhs) and isnum(rhs):
                lhs = lhs.symbol.number
                rhs = rhs.symbol.number
                return ast.SymbolicTerm(x.location, clingo.Number(lhs + rhs if x.name == "+" else lhs - rhs))
            else:
                return ast.BinaryOperation(x.location, op, lhs, rhs)
        elif x.name == "-" and len(x.arguments) == 2:
            return ast.BinaryOperation(x.location, ast.BinaryOperator.Minus, self(x.arguments[0]), self(x.arguments[1]))
        # elif (x.name, TheoryParser.binary) in TheoryParser.table or (x.name, TheoryParser.unary) in TheoryParser.table:
        #     raise RuntimeError("invalid term: {}".format(x.location))
        else:
            return ast.Function(x.location, x.name, [self(a) for a in x.arguments], False)

def theory_term_to_term(x):
    """
    Convert the given theory term into a term.
    """
    return TheoryTermToTermTransformer()(x)


class TheoryTermToLiteralTransformer(Transformer):
    """
    Turns the given theory term into an atom.
    """

    def visit_SymbolicTerm(self, x, positive, sign):
        """
        Maps functions to atoms.

        Every other symbol causes a runtime error.

        Arguments:
        x        -- The theory term to translate.
        positive -- The classical sign of the atom.
        """
        symbol = x.symbol
        if x.symbol.type == clingo.SymbolType.Function and len(symbol.name) > 0:
            atom = astutil.atom(x.location, positive == symbol.positive, symbol.name, [ast.Symbol(x.location, a) for a in symbol.arguments])
            return ast.Literal(x.location, sign, atom)
        else:
            raise RuntimeError("invalid formula: {}".format(x.location))

    def visit_TheoryFunction(self, x, positive, sign):
        """
        Maps theory functions to atoms.

        If the function name is not a negation, an exception is thrown.
        """
        if x.name == "-":
            return self.visit(x.arguments[0], not positive, sign)
        elif positive and (x.name == "not" or x.name == "~"):
            if sign == ast.Sign.Negation:
                return self.visit(x.arguments[0], positive, ast.Sign.DoubleNegation)
            else:
                return self.visit(x.arguments[0], positive, ast.Sign.Negation)
        else:
            atom = astutil.atom(x.location, positive, x.name, [theory_term_to_term(a) for a in x.arguments])
            return ast.Literal(x.location, sign, atom)


def theory_term_to_literal(x, positive=True, sign=ast.Sign.NoSign):
    """
    Convert the given theory term into an literal.
    """
    return TheoryTermToLiteralTransformer()(x, positive, sign)