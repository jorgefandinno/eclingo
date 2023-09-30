import os
import pprint
import subprocess
import textwrap
from collections import namedtuple
from dataclasses import dataclass
from io import StringIO
from pprint import pformat
from typing import Iterable, List, NamedTuple, Optional, Tuple, Union

import clingo
import programs
import programs_helper
from clingo import Function, Symbol
from clingox.testing.ast import parse_term

from eclingo.solver.candidate import Assumptions, Candidate


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format_namedtuple(self, object, stream, indent, allowance, context, level):
        # Code almost equal to _format_dict, see pprint code
        write = stream.write
        write(object.__class__.__name__ + "(")
        object_dict = object._asdict()
        length = len(object_dict)
        if length:
            # We first try to print inline, and if it is too large then we print it on multiple lines
            inline_stream = StringIO()
            self.format_namedtuple_items(
                object_dict.items(),
                inline_stream,
                indent,
                allowance + 1,
                context,
                level,
                inline=True,
            )
            max_width = self._width - indent - allowance
            if len(inline_stream.getvalue()) > max_width:
                self.format_namedtuple_items(
                    object_dict.items(),
                    stream,
                    indent,
                    allowance + 1,
                    context,
                    level,
                    inline=False,
                )
            else:
                stream.write(inline_stream.getvalue())
        write(")")

    def format_namedtuple_items(
        self, items, stream, indent, allowance, context, level, inline=False
    ):
        # Code almost equal to _format_dict_items, see pprint code
        indent += self._indent_per_level
        write = stream.write
        last_index = len(items) - 1
        if inline:
            delimnl = ", "
        else:
            delimnl = ",\n" + " " * indent
            write("\n" + " " * indent)
        for i, (key, ent) in enumerate(items):
            last = i == last_index
            write(key + "=")
            self._format(
                ent,
                stream,
                indent + len(key) + 2,
                allowance if last else 1,
                context,
                level,
            )
            if not last:
                write(delimnl)

    def _format(self, object, stream, indent, allowance, context, level):
        # We dynamically add the types of our namedtuple and namedtuple like
        # classes to the _dispatch object of pprint that maps classes to
        # formatting methods
        # We use a simple criteria (_asdict method) that allows us to use the
        # same formatting on other classes but a more precise one is possible
        if hasattr(object, "_asdict") and type(object).__repr__ not in self._dispatch:
            self._dispatch[type(object).__repr__] = MyPrettyPrinter.format_namedtuple
        super()._format(object, stream, indent, allowance, context, level)


pp = MyPrettyPrinter(indent=4)


def _ast_to_symbol(x: clingo.ast.AST) -> clingo.Symbol:
    """
    Transforms a SymbolicTerm AST of type Function into an AST of type ast.Function.
    """
    if x.ast_type == clingo.ast.ASTType.SymbolicTerm:
        return x.symbol
    if x.ast_type == clingo.ast.ASTType.UnaryOperation:
        a = _ast_to_symbol(x.argument)
        return clingo.symbol.Function(
            a.name,
            a.arguments,
            positive=not a.positive,
        )
    if x.ast_type != clingo.ast.ASTType.Function:
        return x
    return clingo.symbol.Function(
        x.name,
        [_ast_to_symbol(a) for a in x.arguments],
        positive=True,
    )


class ASTtoSymbol(clingo.ast.Transformer):
    """Transforms a SymbolicTerm AST of type Function into an AST of type ast.Function."""

    def visit_SymbolicTerm(self, x: clingo.ast.AST):  # pylint: disable=invalid-name
        return _ast_to_symbol(x)

    def visit_Function(self, x: clingo.ast.AST):  # pylint: disable=invalid-name
        """
        Transforms a SymbolicTerm AST of type Function into an AST of type ast.Function.
        """
        return _ast_to_symbol(x)

    def visit_UnaryOperation(self, x: clingo.ast.AST):  # pylint: disable=invalid-name
        """
        Transforms a SymbolicTerm AST of type Function into an AST of type ast.Function.
        """
        return _ast_to_symbol(x)


ast_to_symbol = ASTtoSymbol()


def build_objective_atom(atom: clingo.ast.AST) -> clingo.symbol.Symbol:
    if atom.name == "not1":
        return clingo.symbol.Function(
            "not1", [clingo.symbol.Function("u", [atom.arguments[0]])]
        )
    return clingo.symbol.Function("u", [atom])


def build_subjective_atom(atom: clingo.ast.AST) -> clingo.symbol.Symbol:
    atom = build_objective_atom(atom.arguments[0])
    return clingo.symbol.Function("k", [atom])


def build_atom(atom: clingo.ast.AST) -> clingo.symbol.Symbol:
    if atom.name == "k":
        return build_subjective_atom(atom)
    return build_objective_atom(atom)


def build_candidate_without_assumptions(candidate: str, assumptions=None) -> Candidate:
    candidate = candidate.strip()
    if not candidate:
        return Candidate(pos=[], neg=[])
    atoms = candidate.split(" ")
    atoms = [parse_term(atom) for atom in atoms]
    atoms = [ast_to_symbol(atom) for atom in atoms]
    pos = [build_subjective_atom(atom) for atom in atoms if atom.name != "no"]
    neg = [
        build_subjective_atom(atom.arguments[0]) for atom in atoms if atom.name == "no"
    ]
    if assumptions is not None:
        return Candidate(pos=pos, neg=neg, extra_assumptions=assumptions)
    return Candidate(pos=pos, neg=neg)


def build_assumptions(assumptions: str) -> Assumptions:
    if not assumptions:
        return Assumptions(pos=[], neg=[])
    atoms = assumptions.split(" ")
    atoms = [ast_to_symbol(parse_term(atom)) for atom in atoms]
    pos = [build_objective_atom(atom) for atom in atoms if atom.name != "no"]
    neg = [
        build_objective_atom(atom.arguments[0]) for atom in atoms if atom.name == "no"
    ]
    return Assumptions(pos=pos, neg=neg)


def build_candidate(
    candidate: Union[str, Tuple[str, str]]
) -> Optional[List[Candidate]]:
    if isinstance(candidate, str):
        return build_candidate_without_assumptions(candidate)
    assumptions = build_assumptions(candidate[1])
    return build_candidate_without_assumptions(candidate[0], assumptions)


def build_candidates(candidates: Optional[Iterable[str]]) -> Optional[List[Candidate]]:
    if candidates is None:
        return None
    return [build_candidate(c) for c in candidates]


def build_preprocessor_result(
    value: Union[str, tuple[str, str]]
) -> Tuple[List[Symbol], List[Symbol]]:
    if isinstance(value, str):
        lower = upper = value
    else:
        lower, upper = value
    lower = lower.strip().split(" ")
    upper = upper.strip().split(" ")
    lower = [build_atom(ast_to_symbol(parse_term(atom))) for atom in lower if atom]
    upper = [build_atom(ast_to_symbol(parse_term(atom))) for atom in upper if atom]
    return lower, upper


def complete_program(program: programs.Program) -> programs_helper.Program:
    new_program_dict = {}
    previous_candidate = None
    for attr, value in sorted(program._asdict().items()):
        if attr != "candidate_wv" and attr.startswith("candidates_"):
            if value is None and previous_candidate is not None:
                new_program_dict[f"{attr}_str"] = new_program_dict[
                    f"{previous_candidate}_str"
                ]
                new_program_dict[attr] = new_program_dict[f"{previous_candidate}"]
            else:
                new_program_dict[f"{attr}_str"] = str(value)
                new_program_dict[attr] = build_candidates(value)
            previous_candidate = attr
        elif attr == "fast_preprocessing":
            if value is None:
                new_program_dict[attr] = None
                new_program_dict[f"{attr}_str"] = None
            else:
                new_program_dict[attr] = build_preprocessor_result(value)
                new_program_dict[f"{attr}_str"] = value
        elif attr == "non_ground_reification" and value is None:
            non_ground_reification = subprocess.check_output(
                f'echo "{program.program}" | eclingo --output-e=rewritten',
                shell=True,
            )
            new_program_dict["non_ground_reification"] = non_ground_reification.decode(
                "utf-8"
            )
        else:
            new_program_dict[attr] = value

    non_ground_reification = new_program_dict["non_ground_reification"]
    if non_ground_reification is not None and program.ground_reification is None:
        ground_reification = subprocess.check_output(
            f'echo "{non_ground_reification}" | clingo --output=reify',
            shell=True,
        )
        new_program_dict["ground_reification"] = ground_reification.decode("utf-8")

    return programs_helper.Program(**new_program_dict)


str_programs = ",\n".join(
    pp.pformat(complete_program(program)) for program in programs.program_list
)

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, "generated_programs.py")
with open(path, "w") as f:
    f.write(
        f'''\
"""
DO NO MODIFY THIS FILE MANUALLY!

This file is generated by tests/build_programs.py
Modify the file "test/programs.py" and run "python test/build_programs.py" instead.
"""


'''
    )
    f.write(
        f"""\
from clingo import Function, Number
from eclingo.solver.candidate import Candidate, Assumptions
from tests.programs_helper import Program

programs = [
{textwrap.indent(str_programs, 4*" ")}
]"""
    )

# for program in programs:
#     program = complete_program(program)
#     print(pp.pformat(program))
#     print()
