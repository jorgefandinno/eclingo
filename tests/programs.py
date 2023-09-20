from clingo import Function

from eclingo.solver.candidate import Assumptions, Candidate
from tests.programs_helper import Program

programs = [
    Program(
        program="a. b :- &k{a}.",
        non_ground_reification="u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates=[
            Candidate(
                pos=[
                    Function(
                        "k", [Function("u", [Function("a", [], True)], True)], True
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        wv_candidates=None,
        unoptimiced_candidates=["k(a)", "not1(k(a))"],
        ground_reification="atom_tuple(0).\n"
        "atom_tuple(0,1).\n"
        "literal_tuple(0).\n"
        "rule(disjunction(0),normal(0)).\n"
        "atom_tuple(1).\n"
        "atom_tuple(1,2).\n"
        "rule(choice(1),normal(0)).\n"
        "atom_tuple(2).\n"
        "atom_tuple(2,3).\n"
        "literal_tuple(1).\n"
        "literal_tuple(1,2).\n"
        "rule(disjunction(2),normal(1)).\n"
        "output(k(u(a)),1).\n"
        "output(u(a),0).\n"
        "literal_tuple(2).\n"
        "literal_tuple(2,3).\n"
        "output(u(b),2).\n",
        description="",
    ),
    Program(
        program="{a}. b :- &k{a}.",
        non_ground_reification="{u(a)}. u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates=[
            Candidate(
                pos=[
                    Function(
                        "k", [Function("u", [Function("a", [], True)], True)], True
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k", [Function("u", [Function("a", [], True)], True)], True
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
        ],
        wv_candidates=None,
        unoptimiced_candidates=["k(a)", "not1(k(a))"],
        ground_reification="atom_tuple(0).\n"
        "atom_tuple(0,1).\n"
        "literal_tuple(0).\n"
        "rule(choice(0),normal(0)).\n"
        "atom_tuple(1).\n"
        "atom_tuple(1,2).\n"
        "literal_tuple(1).\n"
        "literal_tuple(1,1).\n"
        "rule(choice(1),normal(1)).\n"
        "atom_tuple(2).\n"
        "atom_tuple(2,3).\n"
        "literal_tuple(2).\n"
        "literal_tuple(2,2).\n"
        "rule(disjunction(2),normal(2)).\n"
        "output(u(a),1).\n"
        "literal_tuple(3).\n"
        "literal_tuple(3,3).\n"
        "output(u(b),3).\n"
        "output(k(u(a)),2).\n",
        description="",
    ),
]
