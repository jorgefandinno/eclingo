import sys
from typing import Iterator

from eclingo.config import AppConfig
from eclingo.internal_states import internal_control
from eclingo.solver.generator import CandidateGenerator
from eclingo.solver.preprocessor import Preprocessor

from .candidate import Candidate
from .preprocessor import Preprocessor
from .tester import CandidateTester
from .world_view_builder import WorldWiewBuilderWithShow


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
            print("Candidate: ", candidate)
            if self.test_candidate(candidate):
                yield self._build_world_view(candidate)
