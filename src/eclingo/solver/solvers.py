from typing import Iterator

from eclingo.config import AppConfig
from eclingo.solver.generator import GeneratorReification
from eclingo.solver.tester import CandidateTesterReificationWithShow

from .candidate import Candidate
from .world_view_builder import WorldWiewBuilderReification


class SolverReification:
    def __init__(self, reified_program: str, config: AppConfig) -> None:
        self._config = config

        self._build_world_view_reification = WorldWiewBuilderReification()
        self.test_candidate_reification = CandidateTesterReificationWithShow(
            self._config, reified_program
        )
        self.generate_candidates_reification = GeneratorReification(
            self._config, reified_program
        )

    def solve(self) -> Iterator[Candidate]:
        for candidate in self.generate_candidates_reification():
            if self.test_candidate_reification(candidate):
                yield self._build_world_view_reification(candidate)
