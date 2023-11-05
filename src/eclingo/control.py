import sys
import time
from typing import Iterable, Tuple

from clingo import Symbol

from eclingo.config import AppConfig
from eclingo.grounder import Grounder
from eclingo.parsing import parser
from eclingo.solver import SolverReification


def parse_program(stm, parameters=None, name="base"):
    """Helping function to parse program for flag: --output-e=rewritten"""
    if parameters is None:
        parameters = []
    ret = []
    parser.parse_program(
        stm,
        ret.append,
        parameters,
        name,
        config=AppConfig(semantics="c19-1", verbose=0),
    )
    return ret


class Control(object):
    def __init__(self, control, config=None):
        # if control is not None:
        self.project = control.configuration.solve.project
        self.max_models = int(control.configuration.solve.models)
        control.configuration.solve.project = "auto,3"
        control.configuration.solve.models = 0
        self.rewritten_program = []
        self.control = control
        if config is None:
            config = AppConfig(semantics="c19-1")
        self.config = config

        if self.max_models == 0:
            self.max_models = sys.maxsize

        self.grounder = Grounder(self.control, self.config)
        self.models = 0
        self.grounded = False
        self.solver = None
        self.grounding_time = 0
        self.solving_time = 0

    def add_program(self, program):
        if self.config.eclingo_rewritten == "rewritten":
            self.rewritten_program.extend(parse_program(program))
        else:
            self.grounder.add_program(program)

    def load(self, input_path):
        with open(input_path, "r") as program:
            self.add_program(program.read())

    def ground(self, parts: Iterable[Tuple[str, Iterable[Symbol]]] = (("base", []),)):
        start_time = time.time()
        self.grounder.ground(parts)
        self.grounded = True
        self.grounding_time += time.time() - start_time

    def preprocess(self):
        pass

    def prepare_solver(self):
        if not self.grounded:
            self.ground()
        start_time = time.time()
        self.solver = SolverReification(self.grounder.reified_facts, self.config)
        self.grounding_time += time.time() - start_time

    def solve(self):
        if self.solver is None:
            self.prepare_solver()

        start_time = time.time()
        for model in self.solver.solve():
            self.models += 1
            yield model
            if self.models >= self.max_models:
                break
        self.solving_time += time.time() - start_time
