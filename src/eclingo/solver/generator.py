import sys
from typing import Iterator, Optional, Sequence, Tuple, cast

import clingo
from clingo import Function, Symbol
from clingox.backend import SymbolicBackend

from eclingo import util
from eclingo.config import AppConfig
from eclingo.solver.tester import PreprocessingResult

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

atom_map(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
strong_negatation_complement(A, B) :- atom_map(u(SA), A), atom_map(u(-SA), B).
:- hold(A), hold(B), strong_negatation_complement(A, B).

#show positive_candidate/1.
#show negative_candidate/1.
"""

common_opt_program = """\
symbolic_atom(SA) :- atom_map(SA, _).

symbolic_epistemic_atom(k(A)) :- symbolic_atom(k(A)).
symbolic_objective_atom(OSA) :- symbolic_atom(OSA), not symbolic_epistemic_atom(OSA).

epistemic_atom_map(KSA, KA) :- atom_map(KSA, KA), symbolic_epistemic_atom(KSA).
objective_atom_map(OSA, OA) :- atom_map(OSA, OA), symbolic_objective_atom(OSA).

epistemic_atom_int(KA) :- epistemic_atom_map(_, KA).
objective_atom_int(A)  :- objective_atom_map(_, A).

epistemic_map(KA,OA) :- epistemic_atom_map(KSA, KA), objective_atom_map(OSA, OA), KSA = k(OSA).

:- kp_hold(A), epistemic_map(KA, A), not hold(KA).
"""

preprocessing_program = """\
:- cautious(SA), atom_map(SA, A), not hold(A).
positive_extra_assumptions(OSA) :- cautious(OSA), symbolic_epistemic_atom(k(OSA)).
#show positive_extra_assumptions/1.

% hold(A)  :- atom_map(SA, A), cautious_objetive(SA). % this is incorrect, objecti atoms may hold wihtout been proved
% kp_hold(KA) :- epistemic_atom_map(k(SA), KA), cautious_objetive(SA).
"""

# kp_hold(A) :- cautious(SA),  objective_atom_map(SA, A).
# cautious_epistemic(KSA) :- cautious(KSA), symbolic_epistemic_atom(KSA).
# :- epistemic_atom_map(KSA, KA), cautious_epistemic(KSA), not hold(KA).

fact_optimization_program = """\
% Propagate facts into epistemic facts

:- fact(OSA), epistemic_atom_map(k(OSA), KA), not hold(KA).
positive_extra_assumptions(OSA) :- fact(OSA), symbolic_epistemic_atom(k(OSA)).
#show positive_extra_assumptions/1.
"""

propagation_program = """\
kp_hold(OA) :- cautious(OSA),  objective_atom_map(OSA, OA).

singleton_disjuntion(H) :- rule(disjunction(H), _), #count {L : literal_tuple(H, L)} = 1.

kp_conjunction(B) :- literal_tuple(B), kp_hold(A) : literal_tuple(B,  A), A > 0, not epistemic_atom_int(A);
                                          hold(A) : literal_tuple(B,  A), A > 0,     epistemic_atom_int(A);
                                   kp_not_hold(A) : literal_tuple(B, -A), A > 0, not epistemic_atom_int(A);
                                      not hold(A) : literal_tuple(B, -A), A > 0,     epistemic_atom_int(A).

kp_not_conjunction(B) :- literal_tuple(B), kp_not_hold(A), literal_tuple(B, A), A > 0, not epistemic_atom(A).
kp_not_conjunction(B) :- literal_tuple(B),    not hold(A), literal_tuple(B, A), A > 0, epistemic_atom(A).
kp_not_conjunction(B) :- literal_tuple(B), kp_hold(A), literal_tuple(B, -A), A > 0, not epistemic_atom(A).
kp_not_conjunction(B) :- literal_tuple(B),    hold(A), literal_tuple(B, -A), A > 0, epistemic_atom(A).

kp_body(normal(B))     :- rule(_, normal(B)), kp_conjunction(B).
kp_not_body(normal(B)) :- rule(_, normal(B)), kp_not_conjunction(B).

kp_hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), singleton_disjuntion(H), kp_body(B).

rule_head_tuple(H, B) :- rule(disjunction(H), B).
rule_head_tuple(H, B) :- rule(choice(H), B).

kp_not_hold(A) :- symbolic_atom(_, A), kp_not_body(B) : atom_tuple(H,A), rule_head_tuple(H, B).

zhold(SA)        :- hold(A), atom_map(SA, A).
zkp_hold(SA)     :- kp_hold(A), atom_map(SA, A).
zkp_not_hold(SA) :- kp_not_hold(A), atom_map(SA, A).

positive_extra_assumptions(OSA) :-
    kp_hold(OA),
    objective_atom_map(OSA,OA),
    symbolic_epistemic_atom(k(OSA)).
#show positive_extra_assumptions/1.
#show negative_extra_assumptions/1.
"""

# kp_hold(OSA) :- fact(OSA).

#   :- kp_hold(OSA),    objective_atom_map(SA, A).
# % negative_extra_assumptions(SA) :- kp_not_hold(A), epistemic_map(_, A),  objective_atom_map(SA, A).


class GeneratorReification:
    def __init__(
        self,
        config: AppConfig,
        reified_program: str,
        preprocessing_facts: Optional[PreprocessingResult] = None,
    ) -> None:
        self._config = config
        self.control = clingo.Control(["0"], message_limit=0)
        cast(clingo.Configuration, self.control.configuration.solve).project = "show,3"
        self.reified_program = reified_program
        self.__initialeze_control(reified_program, preprocessing_facts)
        self.num_candidates = 0

    def __initialeze_control(self, reified_program, preprocessing_facts) -> None:
        self.control.add("base", [], reified_program)
        self.control.add("base", [], base_program)
        self.control.add("base", [], common_opt_program)
        self.control.add("base", [], fact_optimization_program)
        if self._config.propagate:
            self.control.add("base", [], propagation_program)
        if preprocessing_facts is not None:
            self.control.add("base", [], preprocessing_program)
            with SymbolicBackend(self.control.backend()) as backend:
                for atom in preprocessing_facts.lower:
                    backend.add_rule([Function("cautious", [atom])], [], [])
        self.control.ground([("base", [])])

    def __call__(self) -> Iterator[Candidate]:
        with cast(clingo.SolveHandle, self.control.solve(yield_=True)) as handle:
            for model in handle:
                # print("*"*50)
                # print(model)
                # print("\n".join(sorted(str(a) for a in model.symbols(atoms=True))))
                candidate = self._model_to_candidate(model)
                self.num_candidates += 1
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
