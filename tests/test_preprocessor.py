import textwrap
import unittest
from typing import List

import eclingo
from eclingo.solver.candidate import Candidate
from eclingo.solver.generator import GeneratorReification
from tests.generated_programs import programs


def generate(program):
    config = eclingo.config.AppConfig()
    config.eclingo_semantics = "c19-1"

    candidate_generator = GeneratorReification(config, program)
    candidate_generator.fast_preprocessing()
    candidates = list(candidate_generator())
    # print(sorted(candidates))
    return sorted(candidates)


def format_subtest_message(i: int, program: str, candidates: List[str]) -> str:
    program = textwrap.indent(program, 4 * " ")
    candidates = textwrap.indent("\n".join(candidates), 4 * " ")
    return f"""\

Program {i}:
{program}
Expected candidates:
{candidates}
"""


class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        # discarding assumptiosn from the comparison
        models = [Candidate(pos=m.pos, neg=m.neg) for m in models]
        self.assertCountEqual(models, expected)

    def test_programs(self):
        for i, program in enumerate(programs):
            prg = program.ground_reification
            candidate = program.candidates_02

            if prg is not None and candidate is not None:
                with self.subTest(
                    format_subtest_message(
                        i, program.program, program.candidates_02_str
                    )
                ):
                    self.assert_models(
                        generate(prg),
                        candidate,
                    )
