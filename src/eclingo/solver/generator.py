import sys
from typing import Iterator

import clingo

from eclingo.config import AppConfig
from eclingo.internal_states import internal_control

from .candidate import Candidate


class CandidateGenerator:
    def __init__(
        self, config: AppConfig, control: internal_control.InternalStateControl
    ) -> None:
        self._config = config
        self.control = control
        self._epistemic_literals = (
            self.control.epistemic_to_test_mapping.epistemic_literals()
        )
        with self.control.symbolic_backend() as backend:
            backend.add_project(self._epistemic_literals)

    # TODO: Idea, create a subclass that will call the generator_reification
    # and it will add the rules needed before grounding the new metaprogram + reified terms
    # and later solve
    def __call__(self) -> Iterator[Candidate]:
        with self.control.solve(yield_=True) as handle:
            for model in handle:
                candidate = self.__model_to_candidate(model)
                yield candidate

    def __model_to_candidate(self, model: clingo.Model) -> Candidate:
        candidate_pos = []
        candidate_neg = []
        for epistemic_literal in self._epistemic_literals:
            if model.contains(epistemic_literal):
                candidate_pos.append(epistemic_literal)
            else:
                candidate_neg.append(epistemic_literal)
        return Candidate(candidate_pos, candidate_neg)


# class CandidateGeneratorReification(CandidateGenerator):
# Function to add meta-programming rules

# Function to call the super of call and solve
