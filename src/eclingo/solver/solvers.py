from typing import Iterator

from eclingo.config import AppConfig
from eclingo.solver.generator import GeneratorReification
from eclingo.solver.tester import CandidateTesterReification

from .candidate import Candidate
from .world_view_builder import (
    WorldWiewBuilderReification,
    WorldWiewBuilderReificationWithShow,
)


class SolverReification:
    def __init__(self, reified_program: str, config: AppConfig) -> None:
        self._config = config

        self._build_world_view_reification = WorldWiewBuilderReificationWithShow(
            reified_program
        )
        # self._build_world_view_reification = WorldWiewBuilderReification()
        self.test_candidate_reification = CandidateTesterReification(
            self._config, reified_program
        )
        if self._config.preprocessing_level == 0:  # pragma: no cover
            prepreocessing_info = None
            self.unsatisfiable = False
        else:
            prepreocessing_info = self.test_candidate_reification.fast_preprocessing()
            self.unsatisfiable = prepreocessing_info.unsatisfiable

        self.generate_candidates_reification = GeneratorReification(
            self._config,
            reified_program,
            prepreocessing_info,
        )

    def solve(self) -> Iterator[Candidate]:
        if self.unsatisfiable:
            return []
        for candidate in self.generate_candidates_reification():
            # print(candidate)
            if self.test_candidate_reification(candidate):
                yield self._build_world_view_reification(candidate)

    def number_of_candidates(self) -> int:  # pragma: no cover
        return self.generate_candidates_reification.num_candidates

    def number_of_tester_calls(self) -> int:  # pragma: no cover
        return self.test_candidate_reification.num_solve_calls
