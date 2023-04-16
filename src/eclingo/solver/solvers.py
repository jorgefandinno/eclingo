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

        if self._config.eclingo_reification:
            self._build_world_view_reification = WorldWiewBuilderReification(
                self._control
            )
            self.test_candidate_reification = CandidateTesterReification(
                self._config, self._control.reified_program
            )
            self.generate_candidates_reification = GeneratorReification(
                self._config, self._control.reified_program
            )

        else:
            self._build_world_view = WorldWiewBuilderWithShow(self._control)
            self.test_candidate = CandidateTester(self._config, self._control)
            self.generate_candidates = CandidateGenerator(self._config, self._control)
            self._preprocesor = Preprocessor(self._config, self._control)
            self._preprocesor()

        # (?) Does it need to only be added if using reification?
        # self._preprocesor = Preprocessor(self._config, self._control)
        # self._preprocesor()

    def solve(self) -> Iterator[Candidate]:
        if self._config.eclingo_reification:
            for candidate in self.generate_candidates_reification():
                if self.test_candidate_reification(candidate):
                    print("???")
                    yield self._build_world_view_reification(candidate)
        else:
            for candidate in self.generate_candidates():
                if self.test_candidate(candidate):
                    yield self._build_world_view(candidate)
