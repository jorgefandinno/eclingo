import abc
import textwrap
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple, Union

import clingo
import clingox

from clingo import MessageCode, Symbol, TruthValue
from clingo import ast
from clingo.ast import parse_string

from eclingo.util import astutil
from eclingo.util.groundprogram import ClingoExternal, ClingoOutputAtom, ClingoProject, ClingoRule, ClingoWeightRule, GroundProgram
from clingox import program as clingox_program
from clingox.backend import SymbolicBackend


class ProgramBuilder():

    def __init__(self, control, program):
        self.control = control
        self.program = program
        self.bulider = clingo.ast.ProgramBuilder(self.control)

    def __enter__(self):
        self.bulider.__enter__()
        return self

    def __exit__(self, type_, value, traceback):

        return self.bulider.__exit__(type_, value, traceback)

    def add(self, statement: ast.AST): # pylint: disable=no-member
        self.program.append(statement)
        try:
            return self.bulider.add(statement)
        except RuntimeError as error:
            if len(error.args) != 1:
                raise error
            if error.args[0] == 'literal expected':
                error.args = ('literal expected, got\n' + textwrap.indent(astutil.ast_repr(statement), 13*' '), )
            raise error
        except AttributeError as error:
            if error.args[0] == "'list' object has no attribute 'location'":
                error.args = (error.args[0] + '\n' + textwrap.indent(astutil.ast_repr(statement), 13*' '), )
            raise error

class Control(object):  # type: ignore

    def __init__(self, arguments: Sequence[str] = (), logger: Callable[[MessageCode, str], None] = None, message_limit: int = 20, *, control: clingo.Control = None):
        if control is None:
            control = clingo.Control(arguments, logger, message_limit)
        self.control = control
        self.parsed_program: List[ast.AST] = [] # pylint: disable=no-member
              
        self.ground_program = clingox_program.Program()
        self.control.register_observer(clingox_program.ProgramObserver(self.ground_program))

    def add_program(self, program: str) -> None:
        with self.builder() as builder:
            parse_string(program, builder.add)

    # Done
    def builder(self) -> ProgramBuilder:
        return ProgramBuilder(self.control, self.parsed_program)

    #done
    def ground(self, parts: Sequence[Tuple[str, Sequence[Symbol]]], context: Any = None) -> None:
        self.control.ground(parts, context)

    # done
    def symbolic_backend(self) -> SymbolicBackend:
        return clingox.backend.SymbolicBackend(self.control.backend())

    #def backend(self) -> Backend:
    #    return Backend(self.control.backend(), self.ground_program)

    # def register_observer(self, observer, replace: bool = False) -> None:
    #     return super().register_observer(observer, replace)


    #done
    def add_to(self, control: Union['Control', clingo.Control]):
        program = self.ground_program
        with control.backend() as backend:
            mapping = clingox_program.Remapping(backend, program.output_atoms, program.facts)
            program.add_to_backend(backend, mapping)
        return mapping

    #done
    def facts(self) -> Iterable[Symbol]:
        for symbolic_atom in self.control.symbolic_atoms:
            if symbolic_atom.is_fact:
                yield symbolic_atom.symbol

    #done
    def atom_to_symbol_mapping(self) -> Dict[int, Symbol]:
        mapping = dict()
        for symbolic_atom in self.control.symbolic_atoms:
            if not symbolic_atom.is_fact:
                mapping.update({symbolic_atom.literal : symbolic_atom.symbol})
        return mapping

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.control, attr)


class Observer(clingo.Observer):

    def __init__(self, program):
        self.program = program

    def rule(self, choice: bool, head: Sequence[int], body: Sequence[int]) -> None:
        self.program.objects.append(ClingoRule(choice=choice, head=head, body=body))

    def output_atom(self, symbol: Symbol, atom: int) -> None:
        self.program.objects.append(ClingoOutputAtom(symbol=symbol, atom=atom))

    def weight_rule(self, choice: bool, head: Sequence[int], lower_bound: int, body: Sequence[Tuple[int, int]]) -> None:
        self.program.objects.append(ClingoWeightRule(choice, head, body, lower_bound))

    def project(self, atoms: Sequence[int]) -> None:
        self.program.objects.append(ClingoProject(atoms))

    def external(self, atom: int, value: TruthValue) -> None:
        self.program.objects.append(ClingoExternal(atom, value))


class Application(object):

    @abc.abstractmethod
    def main(self, control: Control, files: Sequence[str]) -> None:
        raise NotImplementedError


class ApplicationWrapper(clingo.Application):
    def __init__(self, application):
        self.application = application

    def main(self, control: clingo.Control, files: Sequence[str]) -> None:
        ext_control = Control(control=control)
        return self.application.main(ext_control, files)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.application, attr)


def clingo_main(application: Application, files: Sequence[str] = ()) -> int:
    return clingo.clingo_main(ApplicationWrapper(application), files)

