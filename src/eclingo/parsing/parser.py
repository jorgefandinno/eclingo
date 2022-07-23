from typing import Callable, Iterable, List, Sequence, cast

from clingo import ast
from clingo.ast import Location, Position

from eclingo import prefixes
from eclingo.config import AppConfig
from eclingo.internal_states.internal_control import ASTObject, ShowStatement
from eclingo.parsing.transformers import ast_reify
from tests.test_reification2 import parse_literal

from .transformers.parser_negations import StrongNegationReplacement
from .transformers.theory_parser_epistemic import (
    double_negate_epistemic_listerals,
    parse_epistemic_literals_elements,
    replace_epistemic_literals_by_auxiliary_atoms,
    replace_negations_by_auxiliary_atoms_in_epistemic_literals,
)

_CallbackType = Callable[[ASTObject], None]

from clingo.ast import ASTType, Location, Position, parse_string
from clingox.ast import (
    TheoryParser,
    prefix_symbolic_atoms,
    reify_symbolic_atoms,
    theory_parser_from_definition,
)


def parse_theory(s: str) -> TheoryParser:
    """
    Turn the given theory into a parser.
    """
    parser = None

    def extract(stm):
        nonlocal parser
        if stm.ast_type == ASTType.TheoryDefinition:
            parser = theory_parser_from_definition(stm)

    parse_string(s, extract)
    return cast(TheoryParser, parser)


class _ProgramParser(object):

    eclingo_theory = """
    #theory eclingo {
    term { not : 0, unary;
           -   : 0, unary;
           ~   : 0, unary
         };
    &k/0 : term, body
    }.
    """

    def __init__(
        self,
        program: str,
        callback: _CallbackType,
        parameters: Sequence[str] = (),
        name: str = "base",
        config: AppConfig = AppConfig(semantics="c19-1"),
    ):
        self.initial_location = Location(
            begin=Position(filename="<string>", line=1, column=1),
            end=Position(filename="<string>", line=1, column=1),
        )
        self.program = program
        self.callback = callback
        self.parameters = [ast.Id(self.initial_location, x) for x in parameters]
        self.name = name
        self.strong_negation_replacements = StrongNegationReplacement()
        self.semantics = config.eclingo_semantics
        self.reification = config.eclingo_reification
        self.theory_parser = parse_theory(_ProgramParser.eclingo_theory)

    def __call__(self) -> None:
        ast.parse_string(self.program, self._parse_statement)
        for aux_rule in self.strong_negation_replacements.get_auxiliary_rules():
            self.callback(aux_rule)

    def _parse_statement(self, statement: ast.AST) -> None:
        statement = self.theory_parser(statement)
        statement = parse_epistemic_literals_elements(statement)

        if self.reification:
            statement = reify_symbolic_atoms(
                statement, prefixes.U_NAME, reify_strong_negation=True
            )
        else:
            statement = prefix_symbolic_atoms(statement, prefixes.U_PREFIX)

        # this avoids collitions between user predicates and auxiliary predicates
        if statement.ast_type == ast.ASTType.Rule:
            for rule in self._parse_rule(statement):
                self.callback(rule)
        elif statement.ast_type == ast.ASTType.Program:
            for statement in self._parse_program_statement(statement):
                self.callback(statement)
        elif statement.ast_type == ast.ASTType.ShowSignature:
            for stm in self._parse_show_signature_statement(statement):
                self.callback(stm)
        elif statement.ast_type == ast.ASTType.ShowTerm:
            raise RuntimeError(
                'syntax error: only show statements of the form "#show atom/n." are allowed.'
            )
        else:
            self.callback(statement)

    def _parse_rule(self, rule: ast.AST) -> Iterable[ast.AST]:
        if self.semantics == "g94":
            rule = double_negate_epistemic_listerals(rule)
        (
            rules,
            sn_replacement,
        ) = replace_negations_by_auxiliary_atoms_in_epistemic_literals(rule)
        self.strong_negation_replacements.update(sn_replacement)

        ret = replace_epistemic_literals_by_auxiliary_atoms(
            rules, self.reification, prefixes.EPISTEMIC_PREFIX
        )

        return ret

    def _parse_program_statement(self, statement: ast.AST) -> List[ast.AST]:
        if (
            statement.name != "base"
            or statement.parameters
            or statement.location != self.initial_location
        ):
            return [statement]

        if self.name == "base" and not self.parameters:
            return [statement]

        new_statement = ast.Program(statement.location, self.name, self.parameters)
        return [statement, new_statement]

    def _parse_show_signature_statement(
        self, statement: ast.AST
    ) -> List[ShowStatement]:
        return [ShowStatement(statement.name, statement.arity, statement.positive)]


#######################################################################################################


def parse_program(
    program: str,
    callback: _CallbackType,
    parameters: Sequence[str] = (),
    name: str = "base",
    config: AppConfig = AppConfig(semantics="c19-1"),
) -> None:
    _ProgramParser(program, callback, parameters, name, config)()
