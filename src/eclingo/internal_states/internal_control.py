from abc import abstractmethod
from dataclasses import dataclass
import textwrap
from typing import Any, Callable, Dict, Iterable, Iterator, List, Sequence, Tuple, Union

import clingo
from clingo import MessageCode, Symbol, SymbolicAtom
from clingo import ast
from clingo.ast import parse_string

from eclingo.prefixes import atom_user_name

from .mappings import EpistemicSymbolToTestSymbolMapping, SymbolToEpistemicLiteralMapping, SymbolToEpistemicLiteralMappingUsingProgramLiterals, SymbolToEpistemicLiteralMappingUsingShowStatements

import clingox
from clingox import program as clingox_program
from clingox.backend import SymbolicBackend

class ASTParsedObject():
    pass

ASTObject = Union[ASTParsedObject, ast.AST]  # pylint: disable=no-member


@dataclass(frozen=True)
class ShowStatement(ASTParsedObject):
    name: str
    arity: int
    poistive: bool

class ShowSignature(set):
    pass


class ProgramBuilder():
            
    def __init__(self, control, show_signature):
        self.control = control
        self.show_signature = show_signature
        self.bulider = clingo.ast.ProgramBuilder(self.control)
        
    def add(self, statement: ASTObject):
        if isinstance(statement, ShowStatement):
            self.show_signature.add(statement)
        elif isinstance(statement, ast.AST):
            return self.bulider.add(statement)
        else:
            raise RuntimeError("Non recognised object: " + str(statement))

    def __enter__(self):
        self.bulider.__enter__()
        return self

    def __exit__(self, type_, value, traceback):
        return self.bulider.__exit__(type_, value, traceback)


class InternalStateControl(object):

    def __init__(self, arguments: Sequence[str] = (), logger: Callable[[MessageCode, str], None] = None, message_limit: int = 20, *, control: clingo.Control = None):
        
        if control is None:
            control = clingo.Control(arguments, logger, message_limit)
        self.control = control
                     
        self.ground_program = clingox_program.Program()
        self.control.register_observer(clingox_program.ProgramObserver(self.ground_program))
        
        # Legacy
        self.show_signature = ShowSignature() # What is this supposed to be doing?
        
        self.epistemic_to_test_mapping = EpistemicSymbolToTestSymbolMapping()
        self.show_mapping = SymbolToEpistemicLiteralMapping()
        
    def add_program(self, program: str) -> None:
        with self.builder() as builder:
            parse_string(program, builder.add)

    def builder(self) -> ProgramBuilder:
        return ProgramBuilder(self.control, self.show_signature)

    def add_to(self, control: Union['InternalStateControl', clingo.Control]):
        program = self.ground_program
        with control.backend() as backend:
            mapping = clingox_program.Remapping(backend, program.output_atoms, program.facts)
            program.add_to_backend(backend, mapping)
        return mapping

    def facts(self) -> Iterable[Symbol]:
        for symbolic_atom in self.control.symbolic_atoms:
            if symbolic_atom.is_fact:
                yield symbolic_atom.symbol
                
    def show_symbols(self) -> Iterator[Symbol]:
        for symbolic_atom in self.show_symbolic_atoms():
            yield symbolic_atom.symbol

    def atom_to_symbol_mapping(self) -> Dict[int, Symbol]:
        mapping = dict()
        for symbolic_atom in self.control.symbolic_atoms:
            if not symbolic_atom.is_fact:
                mapping.update({symbolic_atom.literal : symbolic_atom.symbol})
        return mapping
    
    def show_symbolic_atoms(self) -> Iterator[SymbolicAtom]:
        for show_statement in self.show_signature:
            symbolic_atoms = self.control.symbolic_atoms
            show_statment_user_name = atom_user_name(show_statement.name)
            yield from symbolic_atoms.by_signature(show_statment_user_name, show_statement.arity, show_statement.poistive)

    
    def ground(self, parts: Sequence[Tuple[str, Sequence[Symbol]]], context: Any = None) -> None:
        self.control.ground(parts, context)
        self.epistemic_to_test_mapping = EpistemicSymbolToTestSymbolMapping(self)
        self.show_mapping = self._generate_show_mapping()

    def _generate_show_mapping(self) -> SymbolToEpistemicLiteralMapping:
        if self.show_signature:
            return SymbolToEpistemicLiteralMappingUsingShowStatements(self.show_symbols())
        else:
            return SymbolToEpistemicLiteralMappingUsingProgramLiterals(self.epistemic_to_test_mapping.epistemic_literals())
    

    def symbolic_backend(self) -> SymbolicBackend:
        return clingox.backend.SymbolicBackend(self.control.backend())

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.control, attr)


class Application(object):

    @abstractmethod
    def main(self, control: InternalStateControl, files: Sequence[str]) -> None:
        raise NotImplementedError


class ApplicationWrapper(clingo.Application):
    def __init__(self, application):
        self.application = application

    def main(self, control: clingo.Control, files: Sequence[str]) -> None:
        internal_control = InternalStateControl(control=control)
        return self.application.main(internal_control, files)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.application, attr)


def clingo_main(application: Application, files: Sequence[str] = ()) -> int:
    application_wrapper = ApplicationWrapper(application)
    return clingo.clingo_main(application_wrapper, files)
