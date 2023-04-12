from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Iterator, List, Sequence, Set, Tuple, Union

import clingo
import clingox
from clingo import MessageCode, Symbol, SymbolicAtom, ast
from clingo.ast import parse_string
from clingox import program as clingox_program
from clingox.backend import SymbolicBackend
from clingox.reify import Reifier

from eclingo.config import AppConfig
from eclingo.prefixes import atom_user_name

from .mappings import (
    EpistemicSymbolToTestSymbolMapping,
    SymbolToEpistemicLiteralMapping,
    SymbolToEpistemicLiteralMappingUsingProgramLiterals,
    SymbolToEpistemicLiteralMappingUsingShowStatements,
)


@dataclass(frozen=True)
class ShowStatement:
    name: str
    arity: int
    poistive: bool


ASTObject = Union[ShowStatement, ast.AST]


class ProgramBuilder:
    def __init__(self, control, show_signature: Set[ShowStatement]):
        self.control = control
        self.show_signature = show_signature
        self.bulider = clingo.ast.ProgramBuilder(self.control)

    def add(self, statement: ASTObject):
        if isinstance(statement, ShowStatement):
            return self.show_signature.add(statement)
        return self.bulider.add(statement)

    def __enter__(self):
        self.bulider.__enter__()
        return self

    def __exit__(self, type_, value, traceback):
        return self.bulider.__exit__(type_, value, traceback)


class InternalStateControl(object):
    def __init__(
        self,
        arguments: Sequence[str] = (),
        logger: Callable[[MessageCode, str], None] = None,
        message_limit: int = 20,
        *,
        control: clingo.Control = None,
        config: AppConfig = AppConfig(semantics="c19-1"),
    ):
        if control is None:
            control = clingo.Control(arguments, logger, message_limit)
        self.control = control
        self.config = config
        
        self.ground_program = clingox_program.Program()
        self.control.register_observer(
            clingox_program.ProgramObserver(self.ground_program)
        )
        self.reified_terms: List = []
        self.reified_program: str = ''

        self.show_signature: Set[ShowStatement] = set()

        self.epistemic_to_test_mapping = EpistemicSymbolToTestSymbolMapping()
        self.show_mapping = SymbolToEpistemicLiteralMapping()

    def add_program(self, program: str) -> None:
        with self.builder() as builder:
            parse_string(program, builder.add)
            
    def add_reified_program(self, program) -> None:
        self.reified_program = program
        
    def get_reified_program(self) -> str:
        return self.reified_program

    def builder(self) -> ProgramBuilder:
        return ProgramBuilder(self.control, self.show_signature)

    def add_to(self, control: Union["InternalStateControl", clingo.Control]):
        program = self.ground_program
        with control.backend() as backend:
            mapping = clingox_program.Remapping(
                backend, program.output_atoms, program.facts
            )
            program.add_to_backend(backend, mapping)
        return mapping

    def facts(self) -> Iterable[Symbol]:
        for symbolic_atom in self.control.symbolic_atoms:
            if symbolic_atom.is_fact:
                yield symbolic_atom.symbol

    def show_symbols(self) -> Iterator[Symbol]:
        for symbolic_atom in self.show_symbolic_atoms():
            yield symbolic_atom.symbol

    def show_symbolic_atoms(self) -> Iterator[SymbolicAtom]:
        for show_statement in self.show_signature:
            symbolic_atoms = self.control.symbolic_atoms
            show_statment_user_name = atom_user_name(show_statement.name)
            yield from symbolic_atoms.by_signature(
                show_statment_user_name, show_statement.arity, show_statement.poistive
            )

    def ground(
        self, parts: Sequence[Tuple[str, Sequence[Symbol]]], context: Any = None
    ) -> None:
        self.control.ground(parts, context)

        self.epistemic_to_test_mapping = EpistemicSymbolToTestSymbolMapping(
            self.control.symbolic_atoms
        )
        self.show_mapping = self._generate_show_mapping()

    def _generate_show_mapping(self) -> SymbolToEpistemicLiteralMapping:
        if self.show_signature:
            return SymbolToEpistemicLiteralMappingUsingShowStatements(
                self.show_symbols()
            )
        else:
            return SymbolToEpistemicLiteralMappingUsingProgramLiterals(
                self.epistemic_to_test_mapping.epistemic_literals()
            )

    def symbolic_backend(self) -> SymbolicBackend:
        return clingox.backend.SymbolicBackend(self.control.backend())

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)  # pragma: no cover
        return getattr(self.control, attr)


class Application(object):
    @abstractmethod
    def main(self, control: InternalStateControl, files: Sequence[str]) -> None:
        """
        Function to replace clingo's default main function.
        This function must be implemented.
        """


class ApplicationWrapper(clingo.Application):
    def __init__(self, application):
        self.application = application
        self.program_name = self.application.program_name
        self.version = self.application.version

    def main(self, control: clingo.Control, files: Sequence[str]) -> None:
        internal_control = InternalStateControl(control=control)
        return self.application.main(internal_control, files)

    def register_options(self, options) -> None:
        return self.application.register_options(options)


def clingo_main(application: Application, files: Sequence[str] = ()) -> int:
    application_wrapper = ApplicationWrapper(application)
    return clingo.clingo_main(application_wrapper, files)
