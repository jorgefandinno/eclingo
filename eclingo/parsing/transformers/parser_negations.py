"""
Module to replace strong and default negations by auxiliary atoms.
"""
from copy import copy
from typing import Iterator, List, Set, Tuple

from clingo import ast as _ast  # type: ignore

from . import astutil as _astutil
# from . import transformer as _tf
from clingo.ast import Transformer

# pylint: disable=all

####################################################################################

class SimplifyStrongNegationsTransformer(Transformer):

    def visit_UnaryOperation(self, x):
        if x.operator != _ast.UnaryOperator.Minus:
            raise RuntimeError("invalid term: {}".format(_tf.str_location(x.location)))
        elif x.argument.ast_type == _ast.ASTType.UnaryOperation:
            if x.argument.operator != '-':
                raise RuntimeError("invalid term: {}".format(_tf.str_location(x.location)))
            else:
                return self.visit(x.argument.argument)
        elif x.argument.ast_type != _ast.ASTType.Function:
                raise RuntimeError("invalid term: {}".format(_tf.str_location(x.location)))
        else:
            return x

####################################################################################

def simplify_strong_negations(stm: _ast.AST) -> _ast.AST:
    """
    Removes duplicate occurrences of strong negation and provides
    an equivalent formula.
    """
    return SimplifyStrongNegationsTransformer().visit(stm)

####################################################################################

class StrongNegationToAuxiliarTransformer(Transformer):

    def __init__(self, strong_negation_prefix="sn"):
        self.strong_negation_prefix = strong_negation_prefix
        self.replacement = set()

    def visit_UnaryOperation(self, x):
        if x.operator != _ast.UnaryOperator.Minus:
            raise RuntimeError("invalid term: {}".format(_tf.str_location(x.location)))
        elif x.argument.ast_type != _ast.ASTType.Function:
            raise RuntimeError("invalid term: {}".format(_tf.str_location(x.location)))
        else:
            x = simplify_strong_negations(x)
            name      = x.argument.name
            location  = x.argument.location
            aux_name  = self.strong_negation_prefix + "_" + name
            arguments = x.argument.arguments
            external  = x.argument.external
            atom      = _ast.Function(location, aux_name, arguments, external)
            self.replacement.add((name, len(arguments), aux_name))
            return atom

####################################################################################

class StrongNegationReplacement(Set[Tuple[str, int, str]]):
    
    location = {'begin': {'line': 1, 'column': 1, 'filename': '<replace_strong_negation_by_auxiliary_atoms>'},
                'end':   {'line': 1, 'column': 1, 'filename': '<replace_strong_negation_by_auxiliary_atoms>'}}

    def get_auxiliary_rules(self) -> Iterator[_ast.AST]:
        """
        Returns a rule of the form:
            aux_name(X1, ..., Xn) :- -name(X1, ... , Xn).
        for each tuple in replacement
        """
        for name, arity, aux_name in self:
            yield self._build_auxliary_rule(name, arity, aux_name)

    def _build_auxliary_rule(self, name: str, arity: int, aux_name: str) -> _ast.AST:
        """
        Returns a rule of the form:
            aux_name(X1, ..., Xn) :- -name(X1, ... , Xn).
        where n = arity
        """
        location = StrongNegationReplacement.location
        arguments = []
        for i in range(0, arity):
            var_name = "V" + str(i)
            var = _ast.Variable(location, var_name)
            arguments.append(var)
        head = _astutil.atom(location, True, aux_name, arguments)
        head = _ast.Literal(location, _ast.Sign.NoSign, head)
        body_atom = _astutil.atom(location, False, name, arguments)
        body = [_ast.Literal(location, _ast.Sign.NoSign, body_atom)]
        return _ast.Rule(location, head, body)

SnReplacementType = Set[Tuple[str, int, str]]

def make_strong_negations_auxiliar(stm: _ast.AST) -> Tuple[_ast.AST, SnReplacementType]:
    """
    Replaces strong negation by an auxiliary atom.
    Returns a pair: 
    - the first element is the result of such replacement
    - the second element is a set of triples containing information about the replacement:
      * the first element is the name of the strogly negated atom
      * the second element is its arity
      * the third element is the name of the auxiliary atom that replaces it
    """
    trn = StrongNegationToAuxiliarTransformer()
    stm = trn.visit(stm)
    return (stm, trn.replacement)


def strong_negation_auxiliary_rule(location, name: str, arity: int, aux_name: str) -> _ast.AST:
    """
    Returns a rule of the form:
        aux_name(X1, ..., Xn) :- -name(X1, ... , Xn).
    where n = arity
    """
    arguments = []
    for i in range(0, arity):
        var_name = "V" + str(i)
        var = _ast.Variable(location, var_name)
        arguments.append(var)
    head = _astutil.atom(location, True, aux_name, arguments)
    head = _ast.Literal(location, _ast.Sign.NoSign, head)
    body_atom = _astutil.atom(location, False, name, arguments)
    body = [_ast.Literal(location, _ast.Sign.NoSign, body_atom)]
    return _ast.Rule(location, head, body)


def strong_negation_auxiliary_rule_replacement(replacement: SnReplacementType) -> Iterator[_ast.AST]:
    """
    Returns a rule of the form:
        aux_name(X1, ..., Xn) :- -name(X1, ... , Xn).
    for each tuple in replacement
    """
    location = {'begin': {'line': 1, 'column': 1, 'filename': '<transform>'},
                'end':   {'line': 1, 'column': 1, 'filename': '<transform>'}}
    for name, arity, aux_name in replacement:
        yield strong_negation_auxiliary_rule(location, name, arity, aux_name)


####################################################################################


class DefaultNegationsToAuxiliarTransformer(Transformer):

    def __init__(self, default_negation_prefix="not"):
        self.default_negation_prefix = default_negation_prefix
        self.replacement = []

    def visit_Literal(self, x):
        if x.atom.ast_type == _ast.ASTType.BooleanConstant:
            return x

        atom = self.visit(x.atom)
        if atom is x.atom and (x.sign == _ast.Sign.NoSign):
            return x

        new_x = copy(x)
        new_x.atom = atom

        if new_x.sign == _ast.Sign.NoSign:
            return new_x

        if new_x.sign == _ast.Sign.Negation:
            sign = self.default_negation_prefix + "_"
        elif new_x.sign == _ast.Sign.DoubleNegation:
            sign = self.default_negation_prefix + "2_"
        else:
            sign = ""
       
        location  = atom.term.location
        aux_name  = sign + atom.term.name
        arguments = atom.term.arguments
        external  = atom.term.external
        aux_atom  = _ast.Function(location, aux_name, arguments, external)
        aux_atom  = _ast.SymbolicAtom(aux_atom)
        new_x     = _ast.Literal(location, _ast.Sign.NoSign, aux_atom)
        
        self.replacement.append((x, new_x))
        return new_x


NotReplacementType = List[Tuple[_ast.AST, _ast.AST]]

####################################################################################

def make_default_negation_auxiliar(stm: _ast.AST) -> Tuple[_ast.AST, NotReplacementType]:
    """
    Replaces default negation by an auxiliary atom.
    Returns a pair: 
    - the first element is the result of such replacement
    - the second element is a set of triples containing information about the replacement:
      * the first element is the auxiliary literal replacing the negated literal
      * the second element is the original literal replaced
    """
    # print("make default negation auxillar")
    trn = DefaultNegationsToAuxiliarTransformer()
    stm = trn.visit(stm)
    replacement = trn.replacement
    return (stm, replacement)


def default_negation_auxiliary_rule(location, aux_literal: _ast.AST, original_literal: _ast.AST, gard: List[_ast.AST]) -> _ast.AST:
    """
    Returns a rule of the form:
        aux_literal :- gard, original_literal
    """
    rule_body = list(gard)
    rule_body.append(original_literal)
    return _ast.Rule(location, aux_literal, rule_body)


def default_negation_auxiliary_rule_replacement(location, replacement: NotReplacementType, gard: List[_ast.AST]):
    """
    Returns a rule of the form:
        aux_literal :- gard, original_literal
    for each tuple in replacement
    """
    for original_literal, aux_literal in replacement:
        yield default_negation_auxiliary_rule(location, aux_literal, original_literal, gard)
