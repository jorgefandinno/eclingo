from typing import Dict, List, Sequence, Tuple

from clingo import Symbol
from clingox import program as clingox_program
from clingox.reify import Reifier

from eclingo.config import AppConfig
from eclingo.internal_states.internal_control import InternalStateControl

from .parsing.parser import parse_program


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

    def program_pr(self, program, expected):
        prg_string = []
        for e1, e2 in zip(program, expected):
            prg_string.append(str(e1))

        program = ". ".join(prg_string)
        program = program + "."
        return program

    def add_program(
        self, program: str, parameters: Sequence[str] = (), name: str = "base"
    ) -> None:
        with self.control.builder() as builder:
            parse_program(program, builder.add, parameters, name, self.config)

    def ground(
        self, parts: Sequence[Tuple[str, Sequence[Symbol]]] = (("base", []),)
    ) -> None:  # pylint: disable=dangerous-default-value
        self.control.ground(parts)

    def reification_process(self, program):
        self.add_program(program)
        self.control.register_observer(Reifier(self.temp.append))

        self.ground()
        self.temp = [str(e) for e in self.temp]
        ppp = self.program_pr(self.temp, self.temp)

        print(ppp)

        return ppp
