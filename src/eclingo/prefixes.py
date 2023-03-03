from clingo import Function, Symbol
from clingo.ast import Sign  # pylint: disable=import-error

from eclingo.literals import EpistemicLiteral, Literal

EPISTEMIC_PREFIX = "k_"
NOT_PREFIX = "not_"
NOT2_PREFIX = "not2_"
SN_PREFIX = "sn_"
U_NAME = "u"
U_PREFIX = U_NAME + "_"


def atom_user_name(name: str) -> str:
    return U_PREFIX + name


def atom_not_name(name: str) -> str:
    return NOT_PREFIX + name


def not_symbol(symbol: Symbol) -> Symbol:
    name = atom_not_name(symbol.name)
    return Function(name, symbol.arguments, positive=True)


def original_user_symbol(symbol: Symbol) -> Symbol:
    assert symbol.name.startswith(U_PREFIX)
    name = symbol.name[len(U_PREFIX) :]
    return Function(name, symbol.arguments, symbol.positive)


def symbol_to_epistemic_literal(symbol: Symbol) -> EpistemicLiteral:
    assert symbol.name.startswith(EPISTEMIC_PREFIX)
    name = symbol.name[len(EPISTEMIC_PREFIX) :]

    # if symbol is of the form &k{not L} with L an explicit literal
    if name.startswith(NOT_PREFIX):
        name = name[len(NOT_PREFIX) :]
        sign = Sign.Negation
    # if symbol is of the form &k{not not L} with L an explicit literal
    elif name.startswith(NOT2_PREFIX):
        name = name[len(NOT2_PREFIX) :]
        sign = Sign.DoubleNegation
    # if symbol is of the form &k{L} with L an explicit literal
    else:
        sign = Sign.NoSign

    # L is of the form -a
    symbol_is_explicitely_negated = name.startswith(SN_PREFIX)
    if symbol_is_explicitely_negated:
        name = name[len(SN_PREFIX) :]
    name = name[len(U_PREFIX) :]

    new_symbol = Function(name, symbol.arguments, not symbol_is_explicitely_negated)
    literal = Literal(new_symbol, sign)
    return EpistemicLiteral(literal, Sign.NoSign)


def symbol_to_epistemic_reified_literal(symbol: Symbol) -> EpistemicLiteral:
    assert symbol.name == "k"
    temp_symbol = symbol.arguments[0]
    name = temp_symbol.name

    # if symbol is of the form &k{not L} with L an explicit literal
    if name == "not1":
        name = temp_symbol.arguments[0].name
        sign = Sign.Negation

    # if symbol is of the form &k{not not L} with L an explicit literal
    elif name == "not2":
        name = temp_symbol.arguments[0].name
        sign = Sign.DoubleNegation

    # if symbol is of the form &k{L} with L an explicit literal
    else:
        sign = Sign.NoSign

    # TODO: STILL TO FIX
    # L is of the form -a
    symbol_is_explicitely_negated = name.startswith(SN_PREFIX)
    if symbol_is_explicitely_negated:
        name = name[len(SN_PREFIX) :]

    name = temp_symbol.arguments[0].name
    print("\nThe temp_symbol name: ", temp_symbol.name)

    # TODO: do we want the world view to look like &k{u(a)} or do we want it to look like &k{u(a)} ???

    new_symbol = Function(
        temp_symbol.name, temp_symbol.arguments, not symbol_is_explicitely_negated
    )
    literal = Literal(new_symbol, sign)

    print("\nThe literal: ", literal)
    print()
    return EpistemicLiteral(literal, Sign.NoSign)
