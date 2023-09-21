from typing import cast

import clingo
from clingo.control import Configuration

from eclingo.config import AppConfig

from .candidate import Candidate


class CandidateTesterReification:
    def __init__(self, config: AppConfig, reified_program: str):
        self._config = config
        self.control = clingo.Control(["0"], message_limit=0)
        self.reified_program = reified_program
        cast(Configuration, self.control.configuration.solve).enum_mode = "cautious"  # type: ignore

        program_meta_encoding = """conjunction(B) :- literal_tuple(B),
                                                        hold(L) : literal_tuple(B,  L), L > 0;
                                                    not hold(L) : literal_tuple(B, -L), L > 0.

                                body(normal(B)) :- rule(_, normal(B)), conjunction (B).

                                body(sum(B, G)) :- rule (_sum(B,G)),
                                #sum {
                                    W,L : hold(L), weighted_literal_tuple(B, L,W), L>0;
                                    W,L : not hold(L), weighted_literal_tuple(B, -L,W), L>0} >= G.

                                hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B).

                                {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B).

                                u(A)    :- output(u(A), B), conjunction(B).
                                not1(A) :- output(not1(A), B), conjunction(B).
                                not2(A) :- output(not2(A), B), conjunction(B).


                                symbolic_atom(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
                                epistemic_atom_info(SKA, KA, SA, A) :- symbolic_atom(SA, A), SKA=k(SA), symbolic_atom(SKA, KA).
                                show_statement(SA) :- symbolic_atom(show_statement(SA), _).

                                {k(A)} :- output(k(A), _).

                                hold(L) :- k(A), output(k(A), B), literal_tuple(B, L).
                                :- hold(L) , not k(A), output(k(A), B), literal_tuple(B, L).

                                %%symbolic_atom(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
                                %%epistemic_atom_info(SKA, KA, SA, A) :- symbolic_atom(SA, A), SKA=k(SA), symbolic_atom(SKA, KA).
                                %%show_statement(SA) :- symbolic_atom(show_statement(SA), _).
                                %%hold(L) :  show_statment(SA), output(k(A), B), literal_tuple(B, L).
                                %% #project hold(L) :  output(k(A), B), literal_tuple(B, L).
                                %% #project hold(L) :  show_statment(SA), output(k(A), B), literal_tuple(B, L).
                                """

        self.control.add("base", [], self.reified_program)
        self.control.add("base", [], program_meta_encoding)
        self.control.ground([("base", [])])

    def __call__(self, candidate: Candidate) -> bool:
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        for literal in candidate.pos:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_pos.append(literal)

        for literal in candidate.extra_assumptions.pos:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)

        for literal in candidate.neg:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_neg.append(literal)

        for literal in candidate.extra_assumptions.neg:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)

        cast(Configuration, self.control.configuration.solve).models = 0
        cast(Configuration, self.control.configuration.solve).project = "no"

        # print("\nTESTER")
        # print("Candidate assumptions:\n", candidate_assumptions)
        # print(
        #     "Candidate assumptions:\n",
        #     "\n".join(str((str(a), v)) for a, v in candidate_assumptions),
        # )

        with cast(
            clingo.SolveHandle,
            self.control.solve(yield_=True, assumptions=candidate_assumptions),
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
