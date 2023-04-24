"""
Module to replace strong and default negations by auxiliary atoms.
"""
from copy import copy
from typing import Iterable, Iterator, List, Optional, Set, Tuple

from clingo import ast
from clingo.ast import Location, Position, Transformer
from clingox.ast import reify_symbolic_atoms
from clingox.pprint import pprint

from eclingo import prefixes

from . import ast_reify, astutil

# pylint: disable=all

####################################################################################


# Unused class
class SimplifyStrongNegationsTransformer(Transformer):
    pass


####################################################################################


####################################################################################


class StrongNegationToAuxiliarTransformer(Transformer):
    def __init__(self, use_reification, strong_negation_prefix="sn"):
        self.strong_negation_prefix = strong_negation_prefix
        self.replacement = set()
        self.reification = use_reification

    def visit_UnaryOperation(self, x):
        assert x.operator_type == ast.UnaryOperator.Minus
        assert x.argument.ast_type == ast.ASTType.Function
        x = simplify_strong_negations(x)
        name = x.argument.name

        location = x.argument.location
        arguments = x.argument.arguments
        external = x.argument.external

        if self.reification:
            aux_name = name
        else:
            aux_name = self.strong_negation_prefix + "_" + name
            self.replacement.add((name, len(arguments), aux_name))

        atom = ast.Function(location, aux_name, arguments, external)
        if self.reification:
            return ast.UnaryOperation(location, 0, atom)

        return atom


####################################################################################


class StrongNegationReplacement(Set[Tuple[str, int, str]]):
    location = Location(
        begin=Position(
            filename="<replace_strong_negation_by_auxiliary_atoms>", line=1, column=1
        ),
        end=Position(
            filename="<replace_strong_negation_by_auxiliary_atoms>", line=1, column=1
        ),
    )

    def get_auxiliary_rules(self, reification) -> Iterator[ast.AST]:
        """
        Returns a rule of the form:
            aux_name(X1, ..., Xn) :- -name(X1, ... , Xn).
        for each tuple in replacement
        """
        for name, arity, aux_name in self:
            yield self._build_auxliary_rule(name, arity, aux_name, reification)

    def _build_auxliary_rule(
        self, name: str, arity: int, aux_name: str, reification: bool
    ) -> ast.AST:
        """
        Returns a rule of the form:
            aux_name(X1, ..., Xn) :- -name(X1, ... , Xn).
        where n = arity
        """
        location = StrongNegationReplacement.location
        arguments = []
        for i in range(0, arity):
            var_name = "V" + str(i)
            var = ast.Variable(location, var_name)
            arguments.append(var)
        head = astutil.atom(location, True, aux_name, arguments)
        head = ast.Literal(location, ast.Sign.NoSign, head)
        body_atom = astutil.atom(location, False, name, arguments)
        body = [ast.Literal(location, ast.Sign.NoSign, body_atom)]

        return ast.Rule(location, head, body)


SnReplacementType = Set[Tuple[str, int, str]]


def simplify_strong_negations(stm: ast.AST) -> ast.AST:
    """
    Removes duplicate occurrences of strong negation and provides
    an equivalent formula.
    """
    return SimplifyStrongNegationsTransformer().visit(stm)


def make_strong_negations_auxiliar(
    reification: bool, stm: ast.AST
) -> Tuple[ast.AST, SnReplacementType]:
    """
    Replaces strong negation by an auxiliary atom.
    Returns a pair:
    - the first element is the result of such replacement
    - the second element is a set of triples containing information about the replacement:
      * the first element is the name of the strogly negated atom
      * the second element is its arity
      * the third element is the name of the auxiliary atom that replaces it
    """
    trn = StrongNegationToAuxiliarTransformer(reification)
    stm = trn.visit(stm)
    return (stm, trn.replacement)


####################################################################################


def _make_default_negation_auxiliar(
    reification: bool, stm: ast.AST, default_negation_prefix="not"
) -> ast.AST:
    assert stm.ast_type == ast.ASTType.Literal
    location = stm.atom.symbol.location

    if stm.sign == ast.Sign.NoSign or stm.atom.ast_type != ast.ASTType.SymbolicAtom:
        return stm
    if reification:
        aux_atom = ast_reify.symbolic_literal_to_term(stm)
    else:
        if stm.sign == ast.Sign.Negation:
            sign = default_negation_prefix + "_"
        else:  # stm.sign == ast.Sign.DoubleNegation:
            sign = default_negation_prefix + "2_"

        aux_name = sign + stm.atom.symbol.name
        arguments = stm.atom.symbol.arguments
        external = stm.atom.symbol.external
        aux_atom = ast.Function(location, aux_name, arguments, external)

    aux_atom = ast.SymbolicAtom(aux_atom)
    new_stm = ast.Literal(location, ast.Sign.NoSign, aux_atom)

    return new_stm


NotReplacementType = Optional[Tuple[ast.AST, ast.AST]]


def make_default_negation_auxiliar(
    use_reification: bool, stm: ast.AST
) -> Tuple[ast.AST, NotReplacementType]:
    """
    Replaces default negation by an auxiliary atom.
    Returns a pair:
    - the first element is the result of such replacement
    - the second element is a set of triples containing information about the replacement:
      * the first element is the auxiliary literal replacing the negated literal
      * the second element is the original literal replaced
    """
    assert stm.ast_type == ast.ASTType.TheoryAtomElement
    assert len(stm.terms) == 1
    new_stm = copy(stm)
    lit = new_stm.terms[0]
    new_lit = _make_default_negation_auxiliar(use_reification, lit)
    if new_lit is lit:
        return (new_stm, None)
    new_stm.terms[0] = new_lit
    return (new_stm, (lit, new_lit))


def default_negation_auxiliary_rule(
    location, aux_literal: ast.AST, original_literal: ast.AST, gard: List[ast.AST]
) -> ast.AST:
    """
    Returns a rule of the form:
        aux_literal :- gard, original_literal
    """
    rule_body = list(gard)
    rule_body.append(original_literal)
    return ast.Rule(location, aux_literal, rule_body)


def default_negation_auxiliary_rule_replacement(
    location, replacement: List[ast.AST], gard: List[ast.AST]
):
    """
    Returns a rule of the form:
        aux_literal :- gard, original_literal
    for each tuple in replacement
    """
    for original_literal, aux_literal in replacement:  # type: ignore
        yield default_negation_auxiliary_rule(
            location, aux_literal, original_literal, gard
        )
