from typing import Iterator, cast

import clingo

from eclingo import util
from eclingo.config import AppConfig

from .candidate import Assumptions, Candidate

# from clingox.solving import approximate


class GeneratorReification:
    def __init__(self, config: AppConfig, reified_program: str) -> None:
        self._config = config
        self.control = clingo.Control(["0"], message_limit=0)
        cast(clingo.Configuration, self.control.configuration.solve).project = "show,3"
        self.reified_program = reified_program
        self.__initialeze_control(reified_program)

    def __initialeze_control(self, reified_program) -> None:
        base_program = """
            conjunction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L > 0;
                                            not hold(L) : literal_tuple(B, -L), L > 0.

            body(normal(B)) :- rule(_, normal(B)), conjunction (B).

            body(sum(B, G)) :- rule (_, sum(B,G)),
                               #sum { W,L :     hold(L), weighted_literal_tuple(B,  L, W), L>0;
                                      W,L : not hold(L), weighted_literal_tuple(B, -L, W), L>0} >= G.

            hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B).

            {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B).

            positive_candidate(k(A)) :- output(k(A), B), conjunction(B).
            negative_candidate(k(A)) :- output(k(A), B), not conjunction(B).

            #show positive_candidate/1.
            #show negative_candidate/1.
            """

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

            positive_extra_assumptions(A) :- epistemic_atom(k(A), KA), kp_hold(KA).
            % negative_extra_assumptions(A) :- epistemic_atom(k(A), KA), kp_not_hold(KA).

            #show positive_extra_assumptions/1.
            #show negative_extra_assumptions/1.
            """

        self.control.add("base", [], reified_program)
        self.control.add("base", [], base_program)
        self.control.add("base", [], fact_optimization_program)
        self.control.ground([("base", [])])

    def __call__(self) -> Iterator[Candidate]:
        with cast(clingo.SolveHandle, self.control.solve(yield_=True)) as handle:
            for model in handle:
                candidate = self._model_to_candidate(model)
                yield candidate

    def _model_to_candidate(self, model: clingo.Model) -> Candidate:
        (
            positive_candidate,
            negative_candidate,
            positive_extra_assumptions,
            negative_extra_assumptions,
            _,
        ) = util.partition4(
            model.symbols(shown=True),
            lambda symbol: symbol.name == "positive_candidate",
            lambda symbol: symbol.name == "negative_candidate",
            lambda symbol: symbol.name == "positive_extra_assumptions",
            lambda symbol: symbol.name == "negative_extra_assumptions",
            fun=lambda symbol: symbol.arguments[0],
        )
        extra_assumptions = Assumptions(
            positive_extra_assumptions, negative_extra_assumptions
        )
        return Candidate(positive_candidate, negative_candidate, extra_assumptions)
