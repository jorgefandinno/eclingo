from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Sequence, Set, Tuple, Union

import clingo
from clingo import MessageCode, Symbol, ast
from clingox import program as clingox_program

from eclingo.config import AppConfig


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
        config: AppConfig = AppConfig(semantics="c19-1", use_reification=True),
    ):
        if control is None:
            control = clingo.Control(arguments, logger, message_limit)
        self.control = control
        self.config = config

        self.ground_program = clingox_program.Program()
        self.control.register_observer(
            clingox_program.ProgramObserver(self.ground_program)
        )
        self.show_signature: Set[ShowStatement] = set()

    def builder(self) -> ProgramBuilder:
        return ProgramBuilder(self.control, self.show_signature)

    def ground(
        self, parts: Sequence[Tuple[str, Sequence[Symbol]]], context: Any = None
    ) -> None:
        self.control.ground(parts, context)

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
