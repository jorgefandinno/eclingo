from typing import Iterator

import clingo

from eclingo.config import AppConfig
from eclingo.internal_states import internal_control

from .candidate import Candidate

# class CandidateGenerator:
#     def __init__(
#         self, config: AppConfig, control: internal_control.InternalStateControl
#     ) -> None:
#         self._config = config
#         self.control = control

#     def __call__(self) -> Iterator[Candidate]:
#         with self.control.solve(yield_=True) as handle:
#             for model in handle:
#                 # print("This is the generated model: " + str(model))
#                 candidate = self._model_to_candidate(model)
#                 yield candidate


class GeneratorReification:
    def __init__(self, config: AppConfig, reified_program: str) -> None:
        self._config = config
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)
        self.control.configuration.solve.project = "auto,3"
        self.reified_program = reified_program

    def __call__(self) -> Iterator[Candidate]:
        program2 = """  conjunction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L > 0;
                                                        not hold(L) : literal_tuple(B, -L), L > 0.

                        body(normal(B)) :- rule(_, normal(B)), conjunction (B).

                        body(sum(B, G)) :- rule (_sum(B,G)),
                                           #sum { W,L : hold(L), weighted_literal_tuple(B, L,W), L>0;
                                           W,L : not hold(L), weighted_literal_tuple(B, -L,W), L>0} >= G.

                        hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B).

                        {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B).

                        epistemic(k(A)) :- output(k(A), B), conjunction(B).
                        epistemic(not1(k(A))) :- output(k(A), B), not conjunction(B).

                        #show epistemic/1."""

        self.control.add("base", [], self.reified_program)
        self.control.add("base", [], program2)
        self.control.ground([("base", [])])

        with self.control.solve(yield_=True) as handle:
            for model in handle:
                # print("This is the generated model: " + str(model))
                candidate = self._model_to_candidate(model)
                yield candidate

    def _model_to_candidate(self, model: clingo.Model) -> Candidate:
        candidate_pos = []
        candidate_neg = []

        for symbol in model.symbols(shown=True):
            symbol = symbol.arguments[0]
            if symbol.name == "k":
                # print("Generated Candidate symbol: ", symbol)
                candidate_pos.append(symbol)
            if symbol.name == "not1":
                # print("Generated Candidate symbol Negative: ", symbol)
                candidate_neg.append(symbol.arguments[0])

        # print("Generated candidates: ", Candidate(candidate_pos, candidate_neg), "\n")
        return Candidate(candidate_pos, candidate_neg)
