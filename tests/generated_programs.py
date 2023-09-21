"""
DO NO MODIFY THIS FILE MANUALLY!

This file is generated by tests/build_programs.py
Modify the file "test/programs.py" and run "python test/build_programs.py" instead.
"""


from clingo import Function

from eclingo.solver.candidate import Assumptions, Candidate
from tests.programs_helper import Program

programs = [
    Program(
        program="a. b :- &k{a}.",
        non_ground_reification="u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
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
        candidates_00_str=["k(a)", "not1(k(a))"],
        candidates_00=[
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
        candidates_01_str=["k(a)"],
        candidates_01=[
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
        candidates_02_str=["k(a)"],
        candidates_02=[
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
        candidates_wv_str=["k(a)"],
        candidates_wv=[
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
        description="",
    ),
    Program(
        program="{a}. b :- &k{a}.",
        non_ground_reification="{u(a)}. u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
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
        candidates_00_str=["k(a)", "not1(k(a))"],
        candidates_00=[
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
        candidates_01_str=["k(a)", "not1(k(a))"],
        candidates_01=[
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
        candidates_02_str=["k(a)", "not1(k(a))"],
        candidates_02=[
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
        candidates_wv_str=["k(a)", "not1(k(a))"],
        candidates_wv=[
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
        description="",
    ),
    Program(
        program="{a}. :- not a. b :- &k{a}.",
        non_ground_reification="{u(a)}. :- not u(a). u(b) :- k(u(a)). { k(u(a)) } "
        ":- u(a).",
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
        "atom_tuple(3).\n"
        "literal_tuple(3).\n"
        "literal_tuple(3,-1).\n"
        "rule(disjunction(3),normal(3)).\n"
        "output(u(a),1).\n"
        "literal_tuple(4).\n"
        "literal_tuple(4,3).\n"
        "output(u(b),4).\n"
        "output(k(u(a)),2).\n",
        candidates_00_str=["k(a)", "not1(k(a))"],
        candidates_00=[
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
        candidates_01_str=["k(a)", "not1(k(a))"],
        candidates_01=[
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
        candidates_02_str=["k(a)"],
        candidates_02=[
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
        candidates_wv_str=["k(a)"],
        candidates_wv=[
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
        description="",
    ),
    Program(
        program="{a}. :- a. b :- &k{a}.",
        non_ground_reification="{u(a)}. :- u(a). u(b) :- k(u(a)). { k(u(a)) } :- "
        "u(a).",
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
        "atom_tuple(3).\n"
        "rule(disjunction(3),normal(1)).\n"
        "output(u(a),1).\n"
        "literal_tuple(3).\n"
        "literal_tuple(3,3).\n"
        "output(u(b),3).\n"
        "output(k(u(a)),2).\n",
        candidates_00_str=None,
        candidates_00=None,
        candidates_01_str=["not1(k(a))"],
        candidates_01=[
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k", [Function("u", [Function("a", [], True)], True)], True
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        candidates_02_str=["not1(k(a))"],
        candidates_02=[
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k", [Function("u", [Function("a", [], True)], True)], True
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        candidates_wv_str=["not1(k(a))"],
        candidates_wv=[
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k", [Function("u", [Function("a", [], True)], True)], True
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        description="",
    ),
    Program(
        program="a. b :- &k{not a}.",
        non_ground_reification="u(a). u(b) :- k(not1(u(a))). { k(not1(u(a))) } :- "
        "not1(u(a)). not1(u(a)) :- not u(a).",
        ground_reification="atom_tuple(0).\n"
        "atom_tuple(0,1).\n"
        "literal_tuple(0).\n"
        "rule(disjunction(0),normal(0)).\n"
        "output(u(a),0).\n",
        candidates_00_str=[""],
        candidates_00=[
            Candidate(pos=[], neg=[], extra_assumptions=Assumptions(pos=(), neg=()))
        ],
        candidates_01_str=[""],
        candidates_01=[
            Candidate(pos=[], neg=[], extra_assumptions=Assumptions(pos=(), neg=()))
        ],
        candidates_02_str=[""],
        candidates_02=[
            Candidate(pos=[], neg=[], extra_assumptions=Assumptions(pos=(), neg=()))
        ],
        candidates_wv_str=[""],
        candidates_wv=[
            Candidate(pos=[], neg=[], extra_assumptions=Assumptions(pos=(), neg=()))
        ],
        description="",
    ),
    Program(
        program="{a}. b :- &k{not a}.",
        non_ground_reification="{u(a)}. u(b) :- k(not1(u(a))). { k(not1(u(a))) } "
        ":- not1(u(a)). not1(u(a)) :- not u(a).",
        ground_reification="atom_tuple(0).\n"
        "atom_tuple(0,1).\n"
        "literal_tuple(0).\n"
        "rule(choice(0),normal(0)).\n"
        "atom_tuple(1).\n"
        "atom_tuple(1,2).\n"
        "literal_tuple(1).\n"
        "literal_tuple(1,-1).\n"
        "rule(disjunction(1),normal(1)).\n"
        "atom_tuple(2).\n"
        "atom_tuple(2,3).\n"
        "literal_tuple(2).\n"
        "literal_tuple(2,2).\n"
        "rule(choice(2),normal(2)).\n"
        "atom_tuple(3).\n"
        "atom_tuple(3,4).\n"
        "literal_tuple(3).\n"
        "literal_tuple(3,3).\n"
        "rule(disjunction(3),normal(3)).\n"
        "literal_tuple(4).\n"
        "literal_tuple(4,1).\n"
        "output(u(a),4).\n"
        "literal_tuple(5).\n"
        "literal_tuple(5,4).\n"
        "output(u(b),5).\n"
        "output(k(not1(u(a))),3).\n"
        "output(not1(u(a)),2).\n",
        candidates_00_str=None,
        candidates_00=None,
        candidates_01_str=["k(not1(a))", "not1(k(not1(a)))"],
        candidates_01=[
            Candidate(
                pos=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
        ],
        candidates_02_str=["k(not1(a))", "not1(k(not1(a)))"],
        candidates_02=[
            Candidate(
                pos=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
        ],
        candidates_wv_str=["k(not1(a))", "not1(k(not1(a)))"],
        candidates_wv=[
            Candidate(
                pos=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
        ],
        description="",
    ),
    Program(
        program="{a}. :- not a. b :- &k{not a}.",
        non_ground_reification="{u(a)}. :- not u(a). u(b) :- k(not1(u(a))). { "
        "k(not1(u(a))) } :- not1(u(a)). not1(u(a)) :- not "
        "u(a).",
        ground_reification="atom_tuple(0).\n"
        "atom_tuple(0,1).\n"
        "literal_tuple(0).\n"
        "rule(choice(0),normal(0)).\n"
        "atom_tuple(1).\n"
        "atom_tuple(1,2).\n"
        "literal_tuple(1).\n"
        "literal_tuple(1,-1).\n"
        "rule(disjunction(1),normal(1)).\n"
        "atom_tuple(2).\n"
        "atom_tuple(2,3).\n"
        "literal_tuple(2).\n"
        "literal_tuple(2,2).\n"
        "rule(choice(2),normal(2)).\n"
        "atom_tuple(3).\n"
        "atom_tuple(3,4).\n"
        "literal_tuple(3).\n"
        "literal_tuple(3,3).\n"
        "rule(disjunction(3),normal(3)).\n"
        "atom_tuple(4).\n"
        "rule(disjunction(4),normal(1)).\n"
        "literal_tuple(4).\n"
        "literal_tuple(4,1).\n"
        "output(u(a),4).\n"
        "literal_tuple(5).\n"
        "literal_tuple(5,4).\n"
        "output(u(b),5).\n"
        "output(k(not1(u(a))),3).\n"
        "output(not1(u(a)),2).\n",
        candidates_00_str=None,
        candidates_00=None,
        candidates_01_str=["not1(k(not1(a)))"],
        candidates_01=[
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        candidates_02_str=["not1(k(not1(a)))"],
        candidates_02=[
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        candidates_wv_str=["not1(k(not1(a)))"],
        candidates_wv=[
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        description="",
    ),
    Program(
        program="{a}. :- a. b :- &k{not a}.",
        non_ground_reification="{u(a)}. :- u(a). u(b) :- k(not1(u(a))). { "
        "k(not1(u(a))) } :- not1(u(a)). not1(u(a)) :- not "
        "u(a).",
        ground_reification="atom_tuple(0).\n"
        "atom_tuple(0,1).\n"
        "literal_tuple(0).\n"
        "rule(choice(0),normal(0)).\n"
        "atom_tuple(1).\n"
        "atom_tuple(1,2).\n"
        "literal_tuple(1).\n"
        "literal_tuple(1,-1).\n"
        "rule(disjunction(1),normal(1)).\n"
        "atom_tuple(2).\n"
        "atom_tuple(2,3).\n"
        "literal_tuple(2).\n"
        "literal_tuple(2,2).\n"
        "rule(choice(2),normal(2)).\n"
        "atom_tuple(3).\n"
        "atom_tuple(3,4).\n"
        "literal_tuple(3).\n"
        "literal_tuple(3,3).\n"
        "rule(disjunction(3),normal(3)).\n"
        "atom_tuple(4).\n"
        "literal_tuple(4).\n"
        "literal_tuple(4,1).\n"
        "rule(disjunction(4),normal(4)).\n"
        "output(u(a),4).\n"
        "literal_tuple(5).\n"
        "literal_tuple(5,4).\n"
        "output(u(b),5).\n"
        "output(k(not1(u(a))),3).\n"
        "output(not1(u(a)),2).\n",
        candidates_00_str=None,
        candidates_00=None,
        candidates_01_str=["k(not1(a))", "not1(k(not1(a)))"],
        candidates_01=[
            Candidate(
                pos=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
            Candidate(
                pos=[],
                neg=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                extra_assumptions=Assumptions(pos=(), neg=()),
            ),
        ],
        candidates_02_str=["k(not1(a))"],
        candidates_02=[
            Candidate(
                pos=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        candidates_wv_str=["k(not1(a))"],
        candidates_wv=[
            Candidate(
                pos=[
                    Function(
                        "k",
                        [
                            Function(
                                "not1",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        True,
                    )
                ],
                neg=[],
                extra_assumptions=Assumptions(pos=(), neg=()),
            )
        ],
        description="",
    ),
    Program(
        program="a. b :- not &k{a}.",
        non_ground_reification="u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
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
        candidates_00_str=["k(a)", "not1(k(a))"],
        candidates_00=[
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
        candidates_01_str=["k(a)"],
        candidates_01=[
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
        candidates_02_str=["k(a)"],
        candidates_02=[
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
        candidates_wv_str=["k(a)"],
        candidates_wv=[
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
        description="",
    ),
]
