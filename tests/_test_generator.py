import unittest

import clingo
from clingo.symbol import Function

import eclingo as _eclingo
from eclingo.config import AppConfig
from eclingo.control import Control
from eclingo.solver.candidate import Candidate
from eclingo.solver.generator import CandidateGenerator


class CandidateGeneratorTest(Control):
    def generator_solve(self):
        self.prepare_solver()

        candidates = []
        for candidate in self.solver.generate_candidates():
            candidates.append(candidate)
        return candidates


""" Helper function to generate candidates for a given program """


def generate(program):
    # Initialize
    control = clingo.Control(message_limit=0)
    control.configuration.solve.models = 0
    config = _eclingo.config.AppConfig()
    config.eclingo_semantics = "c19-1"

    control.add_program(program)
    control.ground([("base", [])])

    candidate_generator = CandidateGenerator(config, control)

    candidates = list(candidate_generator())

    return sorted(candidates)


class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(models, expected)


class TestEclingoGenerator(TestCase):
    def test_generator01(self):
        self.assert_models(
            generate("u_b :- k_u_a. u_a. {k_u_a}."),
            [
                Candidate(pos=[], neg=[Function("k_u_a", [], True)]),
                Candidate(pos=[Function("k_u_a", [], True)], neg=[]),
            ],
        )

    # def test_generator02(self):
    #     self.assert_models(generate("u_a. u_b :- k_u_a. u_c :- k_u_b."), [Candidate(pos=[Function('k_u_a', [], True)], neg=[Function('k_u_b', [], True)]), Candidate(pos=[Function('k_u_a', [], True), Function('k_u_b', [], True)], neg=[])])