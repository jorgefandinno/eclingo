import sys
from typing import Iterable, Sequence

import clingo
from clingo import Symbol
from clingox.backend import SymbolicBackend
from clingox.program import Remapping
from clingox.reify import reify_program

import eclingo.internal_states.internal_control as internal_control
from eclingo import internal_states
from eclingo.config import AppConfig

from .candidate import Candidate


class CandidateTester:
    def __init__(
        self, config: AppConfig, control_gen: internal_control.InternalStateControl
    ):
        self._config = config
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)

        if not self._config.eclingo_reification:
            self._epistemic_to_test = control_gen.epistemic_to_test_mapping

            CandidateTester._init_control_test(self.control, control_gen)
            CandidateTester._add_choices_to(
                self.control, self._epistemic_to_test.keys()
            )

        # TODO: Create program and ground like in generator

    @staticmethod
    def _init_control_test(
        control_test: internal_control.InternalStateControl,
        control_gen: internal_control.InternalStateControl,
    ) -> None:
        program = control_gen.ground_program
        with control_test.control.backend() as backend:
            mapping = Remapping(backend, program.output_atoms, program.facts)
            program.add_to_backend(backend, mapping)

        control_test.control.configuration.solve.enum_mode = "cautious"  # type: ignore

    # TODO: Create new add choice to method with
    # {hold(k(A))} :- output(k(A))
    # for reification
    @staticmethod
    def _add_choices_to(
        control_test: internal_control.InternalStateControl, literals: Iterable[Symbol]
    ) -> None:
        with SymbolicBackend(control_test.control.backend()) as backend:
            for literal_code in literals:
                backend.add_rule([literal_code], [], [], True)
                # if self._config.eclingo_project_test:
                #     backend.add_project(
                #         [self._atoms_gen_to_test(signature.test_atom_code)
                #          for signature in self._epistemic_to_test.values()])

    def __call__(self, candidate: Candidate) -> bool:
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        for literal in candidate[0]:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = self._epistemic_to_test[literal]
            candidate_pos.append(literal)

        for literal in candidate[1]:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = self._epistemic_to_test[literal]
            candidate_neg.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                for atom in candidate_pos:
                    if not model.contains(atom):
                        return False

            assert model is not None

            for atom in candidate_neg:
                if model.contains(atom):
                    return False
        return True


class CandidateTesterReification(CandidateTester):
    def __call__(self, candidate: Candidate) -> bool:
        program_meta_encoding = """  conjunction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L > 0;
                                                        not hold(L) : literal_tuple(B, -L), L > 0. 
                                                      
                                    body(normal(B)) :- rule(_, normal(B)), conjunction (B).
                        
                                    body(sum(B, G)) :- rule (_sum(B,G)), 
                                    #sum { 
                                        W,L : hold(L), weighted_literal_tuple(B, L,W), L>0;
                                        W,L : not hold(L), weighted_literal_tuple(B, -L,W), L>0} >= G. 
                                           
                                    hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B). 
                        
                                    {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B). 
    
                                    {hold(A)} :- output(k(A), B).     
                                                   
                                    epistemic(k(A)) :- output(k(A), B), conjunction(B).
                                    epistemic(not1(k(A))) :- output(k(A), B), not conjunction(B).
                                    
                                    #show epistemic/1."""

        self.control.add("base", [], program_meta_encoding)
        self.control.ground([("base", [])])

        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        print("The tester: ", candidate)
        for literal in candidate[0]:  # Positive
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_pos.append(literal)

        for literal in candidate[1]:  # Negative
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_neg.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                for atom in candidate_pos:
                    if not model.contains(atom):
                        return False

            assert model is not None

            for atom in candidate_neg:
                if model.contains(atom):
                    return False
        return True
