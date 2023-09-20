import os
import pprint
import subprocess
import textwrap
from collections import namedtuple
from dataclasses import dataclass
from io import StringIO
from pprint import pformat
from typing import Iterable, List, NamedTuple, Optional

import clingo
import programs
import programs_helper
from clingo import Function
from clingox.testing.ast import parse_term

from eclingo.solver.candidate import Candidate


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
    if x.ast_type != clingo.ast.ASTType.Function:
        return x
    return clingo.symbol.Function(
        x.name,
        [_ast_to_symbol(a) for a in x.arguments],
        positive=True,
    )


class ASTtoSymbol(clingo.ast.Transformer):
    """Transforms a SymbolicTerm AST of type Function into an AST of type ast.Function."""

    def visit_Function(self, x: clingo.ast.AST):  # pylint: disable=invalid-name
        """
        Transforms a SymbolicTerm AST of type Function into an AST of type ast.Function.
        """
        return _ast_to_symbol(x)


def build_candidate_atom(atom: clingo.ast.AST) -> clingo.symbol.Symbol:
    ast_to_symbol = ASTtoSymbol()
    atom = ast_to_symbol(atom)
    atom = clingo.symbol.Function("u", [atom.arguments[0]], True)
    return clingo.symbol.Function("k", [atom], True)


def build_candidate(candidate: str) -> Candidate:
    atoms = candidate.split(" ")
    atoms = [parse_term(atom) for atom in atoms]
    pos = [build_candidate_atom(atom) for atom in atoms if atom.name == "k"]
    neg = [
        build_candidate_atom(atom.arguments[0]) for atom in atoms if atom.name == "not1"
    ]
    return Candidate(pos=pos, neg=neg)


def build_candidates(candidate: Optional[Iterable[str]]) -> Optional[List[Candidate]]:
    if candidate is None:
        return None
    return [build_candidate(c) for c in candidate]


def complete_program(program: programs.Program) -> programs_helper.Program:
    non_ground_reification = program.non_ground_reification
    if non_ground_reification is not None:
        ground_reification = subprocess.check_output(
            f'echo "{non_ground_reification}" | clingo --output=reify',
            shell=True,
        )
        ground_reification = ground_reification.decode("utf-8")

    return programs_helper.Program(
        program=program.program,
        candidates_00_str=program.candidates_00,
        candidates_00=build_candidates(program.candidates_00),
        candidates_01_str=program.candidates_01,
        candidates_01=build_candidates(program.candidates_01),
        candidates_wv_str=program.candidates_wv,
        candidates_wv=program.candidates_wv,
        non_ground_reification=program.non_ground_reification,
        description=program.description,
        ground_reification=ground_reification,
    )


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
from clingo import Function
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
