import sys
from typing import Iterable, Sequence

import clingo
from clingo import Symbol
from clingox.backend import SymbolicBackend
from clingox.program import Remapping
from clingox.reify import reify_program

import eclingo.internal_states.internal_control as internal_control
from eclingo import internal_states
from eclingo.config import AppConfig

from .candidate import Candidate


class CandidateTester:
    def __init__(
        self, config: AppConfig, control_gen: internal_control.InternalStateControl
    ):
        self._config = config
        self._epistemic_to_test = control_gen.epistemic_to_test_mapping
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)
        CandidateTester._init_control_test(self.control, control_gen)
        CandidateTester._add_choices_to(self.control, self._epistemic_to_test.keys())

    @staticmethod
    def _init_control_test(
        control_test: internal_control.InternalStateControl,
        control_gen: internal_control.InternalStateControl,
    ) -> None:
        program = control_gen.ground_program
        with control_test.control.backend() as backend:
            mapping = Remapping(backend, program.output_atoms, program.facts)
            program.add_to_backend(backend, mapping)

        control_test.control.configuration.solve.enum_mode = "cautious"  # type: ignore

    @staticmethod
    def _add_choices_to(
        control_test: internal_control.InternalStateControl, literals: Iterable[Symbol]
    ) -> None:
        with SymbolicBackend(control_test.control.backend()) as backend:
            for literal_code in literals:
                backend.add_rule([literal_code], [], [], True)
                # if self._config.eclingo_project_test:
                #     backend.add_project(
                #         [self._atoms_gen_to_test(signature.test_atom_code)
                #          for signature in self._epistemic_to_test.values()])

    def __call__(self, candidate: Candidate) -> bool:
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        ## TODO: Whenever a candidate with K is sent, it has to do a mapping to u(a) like it does on normal candidates
        print("This the candidate", candidate)
        for literal in candidate[0]:
            #print("no reif", literal)
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = self._epistemic_to_test[literal]
            candidate_pos.append(literal)
            #print("after no reif", literal)  # Gets his u_a removed

        for literal in candidate[1]:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = self._epistemic_to_test[literal]
            candidate_neg.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                print("The model", model)
                for atom in candidate_pos:
                    # print(atom)
                    if not model.contains(atom):
                        return False

            assert model is not None

            for atom in candidate_neg:
                if model.contains(atom):
                    return False
        return True


class CandidateTesterReification(CandidateTester):
    def __call__(self, candidate: Candidate) -> bool:
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        print("This the candidate", candidate)

        ## TODO: Whenever a candidate with K is sent, it has to do a mapping to u(a) like it does on normal candidates
        for literal in candidate[0]:  # Positive
            print("Positive: ", literal)
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            candidate_pos.append(literal)

        for literal in candidate[1]:  # Negative
            print("Negative: ", literal)
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            candidate_neg.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                print("The model", model)
                for atom in candidate_pos:
                    if not model.contains(atom):
                        return False

            assert model is not None

            # print(type(model))
            # for a in model.symbols(shown=True):
            #     print(a.name)

            for atom in candidate_neg:
                # print("The negative candidates: ", candidate_neg)

                if model.contains(atom):
                    return False
        return True
