from collections import namedtuple

from clingo import Function

from eclingo.solver.candidate import Candidate

ua = Function("u", [Function("a", [], True)], True)
kua = Function("k", [ua], True)


Program = namedtuple(
    "Program",
    [
        "description",
        "program",
        "non_ground_reifications",
        "ground_reification",
        "unoptimiced_candidates",
        "candidates",
        "world_views",
    ],
)

programs = [
    Program(
        description="",
        program="a. b :- &k{a}.",
        non_ground_reifications="u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        ground_reification="""\
            tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
            rule(disjunction(0),normal(0)). atom_tuple(1).
            atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
            atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
            rule(disjunction(2),normal(1)). output(k(u(a)),1).
            output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2).
            """,
        unoptimiced_candidates=[
            Candidate(
                pos=[],
                neg=[kua],
            ),
            Candidate(
                pos=[kua],
                neg=[],
            ),
        ],
        candidates=[
            Candidate(
                pos=[kua],
                neg=[],
            )
        ],
        world_views=[],
    ),
]
