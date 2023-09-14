import sys
from typing import Iterable, Sequence, Tuple

from clingo import Symbol
from clingo.ast import parse_string

from eclingo.config import AppConfig
from eclingo.grounder import Grounder
from eclingo.parsing.transformers import function_transformer
from eclingo.solver import SolverReification

from .parsing.transformers.ast_reify import program_to_str


class Control(object):
    def __init__(self, control, config=None):
        # if control is not None:
        self.project = control.configuration.solve.project
        self.max_models = int(control.configuration.solve.models)
        control.configuration.solve.project = "auto,3"
        control.configuration.solve.models = 0
        self.control = control
        # else:
        #     self.project    = None
        #     self.max_models = 1
        #     self.control = internal_states.InternalStateControl(['0', '--project'])
        if config is None:
            config = AppConfig()
        self.config = config

        if self.max_models == 0:
            self.max_models = sys.maxsize

        self.grounder = Grounder(self.control, self.config)
        self.models = 0
        self.grounded = False
        self.solver = None
        self.show_statements: Sequence[Symbol] = []

    def add_program(self, program):
        self.grounder.add_program(program)

    def load(self, input_path):
        with open(input_path, "r") as program:
            self.add_program(program.read())

    def ground(self, parts: Iterable[Tuple[str, Iterable[Symbol]]] = (("base", []),)):
        self.grounder.ground(parts)
        self.grounded = True

    def preprocess(self):
        pass

    def prepare_solver(self):
        if not self.grounded:
            self.ground()

        self.solver = SolverReification(self.grounder.reified_facts, self.config)

    def solve(self):
        if self.solver is None:
            self.prepare_solver()

        for model in self.solver.solve():
            self.models += 1
            yield model
            if self.models >= self.max_models:
                break
