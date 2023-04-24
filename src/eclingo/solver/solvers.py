import sys
from typing import Iterator

from eclingo.config import AppConfig
from eclingo.internal_states import internal_control
from eclingo.solver.generator import CandidateGenerator, GeneratorReification
from eclingo.solver.preprocessor import Preprocessor
from eclingo.solver.tester import CandidateTesterReification

from .candidate import Candidate
from .preprocessor import Preprocessor
from .tester import CandidateTester
from .world_view_builder import WorldWiewBuilderReification, WorldWiewBuilderWithShow


class Solver:
    def __init__(
        self, control: internal_control.InternalStateControl, config: AppConfig
    ) -> None:
        self._control = control
        self._config = config

        self._build_world_view = WorldWiewBuilderWithShow(self._control)
        self.test_candidate = CandidateTester(self._config, self._control)
        self.generate_candidates = CandidateGenerator(self._config, self._control)
        self._preprocesor = Preprocessor(self._config, self._control)
        self._preprocesor()

    def solve(self) -> Iterator[Candidate]:
        for candidate in self.generate_candidates():
            if self.test_candidate(candidate):
                yield self._build_world_view(candidate)


class SolverReification:
    def __init__(self, reified_program: str, config: AppConfig) -> None:
        self._config = config

        self._build_world_view_reification = WorldWiewBuilderReification()
        self.test_candidate_reification = CandidateTesterReification(
            self._config, reified_program
        )
        self.generate_candidates_reification = GeneratorReification(
            self._config, reified_program
        )

    def solve(self) -> Iterator[Candidate]:
        for candidate in self.generate_candidates_reification():
            if self.test_candidate_reification(candidate):
                yield self._build_world_view_reification(candidate)
