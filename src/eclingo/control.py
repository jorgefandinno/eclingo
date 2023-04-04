import sys
from typing import Iterable, Tuple

from clingo import Symbol
from clingo.ast import parse_string
from clingox.reify import Reifier

from eclingo import internal_states
from eclingo.config import AppConfig
from eclingo.grounder import Grounder
from eclingo.parsing.transformers import function_transformer
from eclingo.solver import Solver


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

    # Added later
    def program_pr(self, program, expected):
        prg_string = []
        for e1, e2 in zip(program, expected):
            prg_string.append(str(e1))

        program = " ".join(prg_string)
        return program

    def add_program(self, program):
        # Parsing program TODO: Probably better to add an independent function
        program_org = program
        p = []
        parse_string(program, p.append)
        # print("this is p: ", p)
        program = [function_transformer.rule_to_symbolic_term_adapter(stm) for stm in p]
        # print("\nthis is program: ", program)
        program = self.program_pr(program, program_org)

        program = self.grounder.reification_process(program)

        self.control.add_program(program)  # Originally self.grounder

    # Meaning that:

    # 1. Parse program using Function Transform (Currently on add_program on control.py)
    # 2. Register Observer (on grounder.py on new reification_process function)
    # 3. We call control.ground of the observed reified facts.
    # 4. Parse the temp list (TODO: Porbably better create a callback function independently)
    # 5. the returned program containing the reified facts is added to self.control.add.program and not to the self.grounder.add_program
    # 6. Again, now only one model is being generated. Is missing the rest.

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
