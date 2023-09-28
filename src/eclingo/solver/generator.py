import sys
from typing import Iterator, Optional, Sequence, Tuple, cast

import clingo
from clingo import Function, Symbol
from clingox.backend import SymbolicBackend

from eclingo import util
from eclingo.config import AppConfig

from .candidate import Assumptions, Candidate

# from clingox.solving import approximate


base_program = """\
conjunction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L > 0;
                                not hold(L) : literal_tuple(B, -L), L > 0.

body(normal(B)) :- rule(_, normal(B)), conjunction (B).

body(sum(B, G)) :- rule (_, sum(B,G)),
                    #sum { W,L :     hold(L), weighted_literal_tuple(B,  L, W), L>0;
                            W,L : not hold(L), weighted_literal_tuple(B, -L, W), L>0} >= G.

hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B).

{hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B).

fact(SA) :- output(SA, LT), #count {L : literal_tuple(LT, L)} = 0.

positive_candidate(k(A)) :- fact(k(A)).
positive_candidate(k(A)) :- output(k(A), B), conjunction(B).
negative_candidate(k(A)) :- output(k(A), B), not conjunction(B).

#show positive_candidate/1.
#show negative_candidate/1.
"""

preprocessing_program = """\
atom_map(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
symbolic_atom(SA) :- atom_map(SA, _).

symbolic_epistemic_atom(k(A)) :- symbolic_atom(k(A)).
epistemic_atom_map(KSA, KA) :- atom_map(KSA, KA), symbolic_epistemic_atom(KSA).
epistemic_atom_int(KA) :- epistemic_atom_map(_, KA).

symbolic_objective_atom(OSA) :- symbolic_atom(OSA), not symbolic_epistemic_atom(OSA).

cautious_objetive(SA) :- cautious(SA), symbolic_objective_atom(SA).
%hold(A)  :- atom_map(SA, A), cautious_objetive(SA). % this is incorrect, objecti atoms may hold wihtout been proved
hold(KA) :- epistemic_atom_map(k(SA), KA), cautious_objetive(SA).
"""

fact_optimization_program = """\
% Propagate facts into epistemic facts

symbolic_atom(SA, A) :-
        output(SA,LT),
        #count{LL : literal_tuple(LT, LL)} = 1,
        literal_tuple(LT, A).

epistemic_atom(KSA, KA) :- symbolic_atom(KSA, KA), KSA = k(_).

fact(SA) :-
        output(SA, LT),
        #count {L : literal_tuple(LT, L)} = 0.

pk_hold(KA) :-
    epistemic_atom(SKA, KA),
    SKA = k(SA),
    fact(SA).

hold(KA) :- pk_hold(KA).

positive_extra_assumptions(A) :- epistemic_atom(k(A), KA), pk_hold(KA).
% negative_extra_assumptions(A) :- epistemic_atom(k(A), KA), kp_not_hold(KA).

#show positive_extra_assumptions/1.
#show negative_extra_assumptions/1.
"""


class GeneratorReification:
    def __init__(
        self, config: AppConfig, reified_program: str, preprocessing_facts=None
    ) -> None:
        self._config = config
        self.control = clingo.Control(["0"], message_limit=0)
        cast(clingo.Configuration, self.control.configuration.solve).project = "show,3"
        self.reified_program = reified_program
        self.__initialeze_control(reified_program, preprocessing_facts)
        self.num_candidates = 0

    def __initialeze_control(self, reified_program, preprocessing_facts) -> None:
        # preprocessing_program = """
        #     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #     % A choice is missing here
        #     #external preprocessing.
        #     {k(A)} :- output(k(A), _), preprocessing.
        #     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #     hold_symbolic_atom(SA) :- hold(A), symbolic_atom(SA, A).
        #     hold_symbolic_atom(SA) :- fact(SA).
        #     preprocessing_hold(KA) :- epistemic_atom(k(SA), KA), hold_symbolic_atom(SA).
        #     holds(SA) :- hold(A), symbolic_atom(SA, A).
        #     pk_holds(SA) :- pk_hold(A), symbolic_atom(SA, A).
        # """

        self.control.add("base", [], reified_program)
        self.control.add("base", [], base_program)
        self.control.add("base", [], fact_optimization_program)
        if preprocessing_facts is not None:
            self.control.add("base", [], preprocessing_program)
            with SymbolicBackend(self.control.backend()) as backend:
                for atom in preprocessing_facts.lower:
                    backend.add_rule([Function("cautious", [atom])], [], [])
        self.control.ground([("base", [])])

    # def __initialeze_control_preprocessing(self, preprocessing_facts) -> None:
    #     if preprocessing_facts is None:
    #         return
    #     lower, upper = preprocessing_facts
    #     with self.control.backend() as backend:
    #         for atom in lower:
    #             backend.add_rule([atom], [], [])
    #         # for atom in upper:
    #         #     backend.add_rule([], [], [Function("preprocessing_hold", [atom])])

    def __call__(self) -> Iterator[Candidate]:
        with cast(clingo.SolveHandle, self.control.solve(yield_=True)) as handle:
            for model in handle:
                candidate = self._model_to_candidate(model)
                self.num_candidates += 1
                yield candidate

    def _model_to_candidate(self, model: clingo.Model) -> Candidate:
        # print(" ".join(str(a) for a in sorted(model.symbols(atoms=True))))
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
        # print()
        # print("Model:")
        # print(model)
        # print()
        # print(" ".join(sorted(str(a) for a in model.symbols(atoms=True))))
        return Candidate(positive_candidate, negative_candidate, extra_assumptions)

    # def fast_preprocessing(self) -> None:
    #     print("*" * 50)
    #     solve_limit = self.control.configuration.solve.solve_limit
    #     self.control.configuration.solve.solve_limit = 0
    #     lower_prev_size, upper_pre_size = -1, sys.maxsize
    #     lower_size, upper_size = 0, sys.maxsize
    #     prev_lower, prev_upper = frozenset(), frozenset()
    #     while lower_prev_size < lower_size or upper_pre_size > upper_size:
    #         ret = _approximate(self.control)
    #         if ret is None:
    #             break
    #         lower_all, upper_all = ret
    #         lower = frozenset(
    #             e.arguments[0] for e in lower_all if e.name == "preprocessing_hold"
    #         )
    #         upper = frozenset(
    #             e.arguments[0] for e in upper_all if e.name == "preprocessing_hold"
    #         )
    #         lower_prev_size, upper_pre_size = lower_size, upper_size
    #         lower_size, upper_size = len(lower), len(upper)

    #         print("-" * 50)
    #         names = {"holds", "pk_holds", "preprocessing_hold"}
    #         print(
    #             f"lower ({lower_prev_size},{lower_size}):\n",
    #             " ".join(str(e) for e in sorted(lower_all) if e.name in sorted(names)),
    #         )
    #         # # print(f"lower ({lower_prev_size},{lower_size}):\n", " ".join(str(e) for e in sorted(lower_all)))
    #         print(
    #             f"upper ({upper_pre_size},{upper_size}):\n",
    #             " ".join(str(e) for e in sorted(upper_all) if e.name in names),
    #         )

    #         if lower_prev_size < lower_size:
    #             lower_diff = lower.difference(prev_lower)
    #             print("lower_diff ", lower_diff)
    #             with SymbolicBackend(self.control.backend()) as symbolic_backend:
    #                 for atom in lower_diff:
    #                     symbolic_backend.add_rule([], [], [Function("hold", [atom])])

    #     self.control.configuration.solve.solve_limit = solve_limit
