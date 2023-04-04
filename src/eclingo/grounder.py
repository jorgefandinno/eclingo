from typing import Dict, List, Sequence, Tuple

from clingo import Symbol
from clingox import program as clingox_program
from clingox.reify import Reifier

from eclingo.config import AppConfig
from eclingo.internal_states.internal_control import InternalStateControl

from .parsing.parser import parse_program
from .parsing.transformers.ast_reify import reification_program_to_str


class Grounder:
    def __init__(self, control: InternalStateControl, config: AppConfig = AppConfig()):
        self.control = control
        self.config = config
        self.reification = self.config.eclingo_reification
        self.facts: List[Symbol] = []
        self.epistemic_facts: List[Symbol] = []
        self.atom_to_symbol: Dict[int, Symbol] = dict()
        self.ground_program = clingox_program.Program()
        self.control.register_observer(
            clingox_program.ProgramObserver(self.ground_program)
        )
        self.temp = []

    def add_program(
        self, program: str, parameters: Sequence[str] = (), name: str = "base"
    ) -> None:
        with self.control.builder() as builder:
            parse_program(program, builder.add, parameters, name, self.config)

    def ground(
        self, parts: Sequence[Tuple[str, Sequence[Symbol]]] = (("base", []),)
    ) -> None:  # pylint: disable=dangerous-default-value
        self.control.ground(parts)

    # TODO: Make this function look better.
    # Probable create a callback function rather than a list
    def create_reified_facts(self, program):
        self.add_program(program)
        self.control.register_observer(Reifier(self.temp.append))

        self.ground()
        self.temp = [str(e) for e in self.temp]
        reified_facts = reification_program_to_str(self.temp)

        print("The reified facts are: ", reified_facts)

        return reified_facts
