from typing import Iterator

import clingo

from eclingo.config import AppConfig
from eclingo.internal_states import internal_control

from .candidate import Candidate


class GeneratorReification:
    def __init__(self, config: AppConfig, reified_program: str) -> None:
        self._config = config
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)
        self.control.configuration.solve.project = "auto,3"
        self.reified_program = reified_program

    def __call__(self) -> Iterator[Candidate]:
        base_program = """
            conjunction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L > 0;
                                            not hold(L) : literal_tuple(B, -L), L > 0.

            body(normal(B)) :- rule(_, normal(B)), conjunction (B).

            body(sum(B, G)) :- rule (_sum(B,G)),
                                #sum { W,L : hold(L), weighted_literal_tuple(B, L,W), L>0;
                                W,L : not hold(L), weighted_literal_tuple(B, -L,W), L>0} >= G.

            hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B).

            {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B).

            positive_candidate(k(A)) :- output(k(A), B), conjunction(B).
            negative_candidate(k(A)) :- output(k(A), B), not conjunction(B).

            #show positive_candidate/1.
            #show negative_candidate/1."""

        fact_optimization_program = """
            % Propagate facts into epistemic facts

            symbolic_atom(SA, A) :-
                    output(SA,LT),
                    #count{LL : literal_tuple(LT, LL)} = 1,
                    literal_tuple(LT, A).

            epistemic_atom(KSA, KA) :- symbolic_atom(KSA, KA), KSA = k(_).

            fact(SA) :-
                    output(SA, LT),
                    #count {L : literal_tuple(LT, L)} = 0.

            kp_hold(KA) :-
                epistemic_atom(SKA, KA),
                SKA = k(SA),
                fact(SA).

            hold(KA) :- kp_hold(KA).
            """

        self.control.add("base", [], self.reified_program)
        self.control.add("base", [], base_program)
        self.control.add("base", [], fact_optimization_program)
        self.control.ground([("base", [])])

        with self.control.solve(yield_=True) as handle:
            for model in handle:
                candidate = self._model_to_candidate(model)
                yield candidate

    def _model_to_candidate(self, model: clingo.Model) -> Candidate:
        # positive_candidate = []
        # negative_candidate = []

        # for symbol in model.symbols(shown=True):
        #     if symbol.name == "positive_candidate":
        #         positive_candidate.append(symbol.arguments[0])
        #     if symbol.name == "negative_candidate":
        #         negative_candidate.append(symbol.arguments[0])

        symbols = model.symbols(shown=True)
        # We should be able to change this by tuples, but test currently fail if so
        positive_candidate = [
            symbol.arguments[0]
            for symbol in symbols
            if symbol.name == "positive_candidate"
        ]
        negative_candidate = [
            symbol.arguments[0]
            for symbol in symbols
            if symbol.name == "negative_candidate"
        ]

        # print("Generated candidates: ", Candidate(candidate_pos, candidate_neg), "\n")
        return Candidate(positive_candidate, negative_candidate)
