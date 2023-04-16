import unittest

from clingo.symbol import Function

import eclingo as _eclingo
from eclingo.solver.candidate import Candidate
from eclingo.solver.tester import CandidateTesterReification


""" Helper function to generate candidates for a given program and test them"""
def tester(program, candidates):

    config = _eclingo.config.AppConfig()
    config.eclingo_semantics = "c19-1"

    test_candidate = CandidateTesterReification(config, program)
    tested = []
    for candidate in candidates:
        print("Test Tested candidate: ", candidate)
        if test_candidate(candidate):
            if candidate not in tested:
                tested.append(candidate)

    return sorted(tested)


class TestCase(unittest.TestCase):
    def assert_models(self, candidates, expected):
        self.assertEqual(candidates, expected)


class TestEclingoTesterReification(TestCase):
    def test_tester_reification(self):
        # echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
        # "a. b :- &k{a}."
        self.assert_models(
            tester(
                """tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                    rule(disjunction(0),normal(0)). atom_tuple(1).
                                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                    atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
                                    rule(disjunction(2),normal(1)). output(k(u(a)),1).
                                    output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2).""",
                [
                    Candidate(
                        pos=[],
                        neg=[
                            Function(
                                "k",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                    ),
                    Candidate(
                        pos=[
                            Function(
                                "k",
                                [Function("u", [Function("a", [], True)], True)],
                                True,
                            )
                        ],
                        neg=[],
                    ),
                ],
            ),
            [
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], True)], True)], True
                        )
                    ],
                    neg=[],
                )
            ],
        )

    def test_tester_reification_double_negation(self):
        # echo "a. b :- &k{ not not a }." | eclingo --output=reify --semantics c19-1 --reification
        self.assert_models(
            tester(
                """tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)). 
                        atom_tuple(1). atom_tuple(1,2). rule(disjunction(1),normal(0)). atom_tuple(2). atom_tuple(2,3). 
                        rule(choice(2),normal(0)). atom_tuple(3). atom_tuple(3,4). literal_tuple(1). literal_tuple(1,3). 
                        rule(disjunction(3),normal(1)). output(k(not2(u(a))),1). output(u(a),0). literal_tuple(2).
                        literal_tuple(2,4). output(u(b),2). output(not2(u(a)),0). rule(choice(2),normal(0)). 
                        rule(disjunction(3),normal(1)).""",
                [
                    Candidate(
                        pos=[],
                        neg=[
                            Function(
                                "k",
                                [
                                    Function(
                                        "not2",
                                        [
                                            Function(
                                                "u", [Function("a", [], True)], True
                                            )
                                        ],
                                        True,
                                    )
                                ],
                                True,
                            )
                        ],
                    )
                ],
            ),
            [
                Candidate(
                    pos=[],
                    neg=[
                        Function(
                            "k",
                            [
                                Function(
                                    "not2",
                                    [Function("u", [Function("a", [], True)], True)],
                                    True,
                                )
                            ],
                            True,
                        )
                    ],
                )
            ],
        )

    def test_tester_reification_explicit_negation(self):
        # echo "-a. b:- &k{-a}. c :- b." | eclingo --semantics c19-1 --reification --output=reify
        self.assert_models(
            tester(
                """tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)). 
                    atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2). atom_tuple(2,3). 
                    literal_tuple(1). literal_tuple(1,2). rule(disjunction(2),normal(1)). atom_tuple(3). atom_tuple(3,4). 
                    literal_tuple(2). literal_tuple(2,3). rule(disjunction(3),normal(2)). output(k(u(-a)),1).
                    output(u(-a),0). output(u(b),2). literal_tuple(3). literal_tuple(3,4). output(u(c),3). 
                    rule(choice(1),normal(0)). rule(disjunction(2),normal(1)). rule(disjunction(3),normal(2)).""",
                [
                    Candidate(
                        pos=[],
                        neg=[
                            Function(
                                'k', [Function('u', [Function('a', [], False)], True)], True
                            )
                        ]
                    ),
                    Candidate(
                        pos=[
                            Function(
                                'k', [Function('u', [Function('a', [], False)], True)], True
                            )
                        ],
                        neg=[]
                    ),
                ],
            ),
            [
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        )
                    ],
                    neg=[],
                )
            ],
        )
   
    def test_tester_reification_explicit_negation02(self):
    # echo "u(-a). u(b) :- k(u(-a)). {k(u(-a))}." | clingo --output=reify
    # echo "-a. b :- &k{-a}." | eclingo --semantics c19-1 --reification --output=reify
        self.assert_models(
                tester(
                    """atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)). atom_tuple(1).
                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2). atom_tuple(2,3). literal_tuple(1). 
                    literal_tuple(1,2). rule(disjunction(2),normal(1)). output(k(u(-a)),1). output(u(-a),0). literal_tuple(2).
                    literal_tuple(2,3). output(u(b),2).""",
                    
                    [
                        Candidate(
                            pos=[
                                Function(
                                    'k', [Function('u', [Function('a', [], False)], True)], True
                                )
                            ],
                            neg=[],
                        )
                    ],
                ),
                [
                    Candidate(
                        pos=[
                            Function(
                                'k', [Function('u', [Function('a', [], False)], True)], True
                            )
                        ],
                        neg=[],
                    )
                ],
            )
    
