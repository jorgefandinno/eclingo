from typing import Dict, Iterable, List, NamedTuple, Sequence, Tuple, Union

import clingo  # type: ignore
from clingo import Symbol

import clingox
from clingox import program as clingox_program
from eclingo.config import AppConfig
from eclingo.literals import Literal

from .internal_states import InternalStateControl
from .parsing.parser import parse_program

CONTROL = Union[clingo.Control, InternalStateControl]

class EpistemicSignature(NamedTuple):
    epistemic_literal: Symbol
    code: int
    literal: Literal
    test_atom: Symbol
    test_atom_code: int


class Grounder():

    def __init__(self, control: InternalStateControl, config: AppConfig = AppConfig()):
        self.control = control
        self.config = config
        self.facts: List[Symbol]           = []
        self.epistemic_facts: List[Symbol] = []
        self.atom_to_symbol: Dict[int, Symbol] = dict()
        self.symbol_to_atom: Dict[Symbol, int] = dict()
        self.epistemic_signature: Dict[int, EpistemicSignature] = dict()
        self.ground_program = clingox_program.Program()
        self.control.register_observer(clingox_program.ProgramObserver(self.ground_program))


    def add_program(self, program: str, parameters: List[str] = [], name: str = "base") -> None: # pylint: disable=dangerous-default-value
        with self.control.builder() as builder:
            parse_program(program, builder.add, parameters, name, self.config.eclingo_semantics)


    def ground(self, parts: Sequence[Tuple[str, Sequence[Symbol]]] = (("base", []),)) -> None: # pylint: disable=dangerous-default-value
        self.control.ground(parts)