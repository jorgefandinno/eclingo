import sys
from typing import Iterable, Tuple

from clingo import Symbol
from clingo.ast import parse_string

from eclingo.config import AppConfig
from eclingo.grounder import Grounder
from eclingo.parsing.transformers import function_transformer
from eclingo.solver import Solver

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
        # self.reified_program = ''

    def reification_parse_program(self, program):
        p = []
        parse_string(program, p.append)
        program = [function_transformer.rule_to_symbolic_term_adapter(stm) for stm in p]
        program = program_to_str(program)

        program = self.grounder.create_reified_facts(program)
        self.grounded = True
        return program

    def add_program(self, program):
        if self.config.eclingo_reification:
            program = self.reification_parse_program(program)
            self.control.add_reified_program(program)
        else:
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

        self.solver = Solver(self.control, self.config)

    def solve(self):
        if self.solver is None:
            self.prepare_solver()

        for model in self.solver.solve():
            self.models += 1
            yield model
            if self.models >= self.max_models:
                break
