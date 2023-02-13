from typing import Dict, Iterable, List, NamedTuple, Sequence, Tuple, Union

from clingo import Symbol
from clingox import program as clingox_program
from clingox.reify import Reifier, reify_program

from eclingo.config import AppConfig
from eclingo.internal_states.internal_control import InternalStateControl

from .parsing.parser import parse_program


class Grounder:
    def __init__(self, control: InternalStateControl, config: AppConfig = AppConfig()):
        self.control = control
        self.config = config
        self.facts: List[Symbol] = []
        self.epistemic_facts: List[Symbol] = []
        self.atom_to_symbol: Dict[int, Symbol] = dict()
        self.ground_program = clingox_program.Program()
        self.control.register_observer(
            clingox_program.ProgramObserver(self.ground_program)
        )

    def add_program(
        self, program: str, parameters: Sequence[str] = (), name: str = "base"
    ) -> None:
        with self.control.builder() as builder:
            parse_program(program, builder.add, parameters, name, self.config)

    def ground(
        self, parts: Sequence[Tuple[str, Sequence[Symbol]]] = (("base", []),)
    ) -> None:  # pylint: disable=dangerous-default-value
        self.control.ground(parts)
