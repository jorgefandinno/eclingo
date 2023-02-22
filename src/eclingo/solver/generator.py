import sys
from typing import Iterator

import clingo

import eclingo
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

    def __call__(self) -> Iterator[Candidate]:
        with self.control.solve(yield_=True) as handle:
            for model in handle:
                print("This is the generated model: " + str(model))
                candidate = self._model_to_candidate(model)
                yield candidate

    def _model_to_candidate(self, model: clingo.Model) -> Candidate:
        candidate_pos = []
        candidate_neg = []
        for epistemic_literal in self._epistemic_literals:
            if model.contains(epistemic_literal):
                candidate_pos.append(epistemic_literal)
            else:
                candidate_neg.append(epistemic_literal)
        return Candidate(candidate_pos, candidate_neg)

# echo ":- &k{a}. a." | eclingo --output=reify --reification --semantics c19-1
# echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
# echo "a. b :- &k{a}." | eclingo  --semantics c19-1 --reification

# eclingo pr1.lp --semantics c19-1
# eclingo pr1.lp --semantics c19-1 --reification Still works, but gives me no world views, nor the whole generated models.


class GeneratorReification(CandidateGenerator):
    def __call__(self) -> Iterator[Candidate]:
        program2 = """  conjunction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L > 0;
                                                        not hold(L) : literal_tuple(B, -L), L > 0. 
                                                      
                        body(normal(B)) :- rule(_, normal(B)), conjunction (B).
                        
                        body(sum(B, G)) :- rule (_sum(B,G)), 
                                           #sum { W,L : hold(L), weighted_literal_tuple(B, L,W), L>0; W,L : not hold(L), weighted_literal_tuple(B, -L,W), L>0} >= G. 
                                           
                        hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B). 
                        
                        {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B). 
                        
                        show(k(A)) :- output(k(A), B), conjunction(B).
                        show(not1(k(A))) :- output(k(A), B), not conjunction(B).
                        
                        #show T : show(T)."""

        self.control.add("base", [], program2)
        self.control.ground([("base", [])])

        return super().__call__()

    def _model_to_candidate(self, model: clingo.Model) -> Candidate:
        candidate_pos = []
        candidate_neg = []

        print(model.symbols(shown=True))
        for symbol in model.symbols(shown=True):
            if symbol.name == "k":
                candidate_pos.append(symbol)
            if symbol.name == "not1":
                candidate_neg.append(symbol.arguments[0])

        return Candidate(candidate_pos, candidate_neg)
