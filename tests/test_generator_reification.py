import unittest

from clingo.symbol import Function

import eclingo as _eclingo
from eclingo.solver.candidate import Candidate
from eclingo.solver.generator import GeneratorReification

from .programs import programs

# python -m unittest tests.test_generator_reification.TestEclingoGeneratorReification

""" Helper function to generate candidates for a given program """


def generate(program):

    config = _eclingo.config.AppConfig()
    config.eclingo_semantics = "c19-1"

    candidate_generator = GeneratorReification(config, program)

    candidates = list(candidate_generator())
    # print(sorted(candidates))
    return sorted(candidates)


class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        # discarding assumptiosn from the comparison
        models = [Candidate(pos=m.pos, neg=m.neg) for m in models]
        self.assertCountEqual(models, expected)


class TestEclingoGeneratorReification(TestCase):
    # "a. b :- &k{a}."
    # echo "u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a)." | clingo --output=reify
    def test_generator01_reification(self):
        self.assert_models(
            generate(programs[0].ground_reification),
            programs[0].candidates,
        )

        # "{a}. b :- &k{a}."
        # echo "{u(a)}. u(b) :- k(u(a)). { k(u(a)) } :- u(a)." | clingo --output=reify
        self.assert_models(
            generate(programs[1].ground_reification),
            programs[1].candidates,
        )

        self.assert_models(
            generate(
                """atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(choice(0),normal(0)).
                                    atom_tuple(1). atom_tuple(1,2). literal_tuple(1). literal_tuple(1,1).
                                    rule(choice(1),normal(1)). atom_tuple(2). atom_tuple(2,3). literal_tuple(2).
                                    literal_tuple(2,2). rule(disjunction(2),normal(2)). atom_tuple(3). literal_tuple(3).
                                    literal_tuple(3,-1). rule(disjunction(3),normal(3)). output(u(a),1). literal_tuple(4).
                                    literal_tuple(4,3). output(u(b),4). output(k(u(a)),2)."""
            ),
            [
                Candidate(
                    pos=[],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("a", [], True)], True)], True
                        )
                    ],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], True)], True)], True
                        )
                    ],
                    neg=[],
                ),
            ],
        )

        # echo "u(-a). u(b) :- k(u(-a)). u(c) :- k(u(b)). {k(u(-a))}. {k(u(b))}." | clingo --output=reify
        self.assert_models(
            generate(
                """atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)).
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                  atom_tuple(2,3). rule(choice(2),normal(0)). atom_tuple(3). atom_tuple(3,4). literal_tuple(1).
                                  literal_tuple(1,2). rule(disjunction(3),normal(1)). atom_tuple(4). atom_tuple(4,5).
                                  literal_tuple(2). literal_tuple(2,3). rule(disjunction(4),normal(2)). output(k(u(b)),1).
                                  output(k(u(-a)),2). output(u(-a),0). literal_tuple(3). literal_tuple(3,4).
                                  output(u(c),3). literal_tuple(4). literal_tuple(4,5). output(u(b),4)."""
            ),
            [
                # Candidate(pos=[], neg=[Function('k', [Function('u', [Function('b', [], True)], True)], True),
                #                        Function('k', [Function('u', [Function('a', [], False)], True)], True)]),
                # Candidate(pos=[Function('k', [Function('u', [Function('b', [], True)], True)], True)],
                #           neg=[Function('k', [Function('u', [Function('a', [], False)], True)], True)]),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        ),
                    ],
                    neg=[],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        )
                    ],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        )
                    ],
                ),
            ],
        )

        # echo "{u(-a)}. u(b) :- k(u(-a)). u(c) :- k(u(b)). {k(u(-a))}. {k(u(b))}." | clingo --output=reify
        self.assert_models(
            generate(
                """atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(choice(0),normal(0)).
                            atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                            atom_tuple(2,3). literal_tuple(1). literal_tuple(1,1). rule(disjunction(2),normal(1)).
                            atom_tuple(3). atom_tuple(3,4). literal_tuple(2). literal_tuple(2,2).
                            rule(disjunction(3),normal(2)). atom_tuple(4). atom_tuple(4,5).
                            rule(choice(4),normal(0)). literal_tuple(3). literal_tuple(3,3).
                            output(u(c),3). literal_tuple(4). literal_tuple(4,4). output(u(b),4).
                            literal_tuple(5). literal_tuple(5,5). output(u(-a),5). output(k(u(b)),1).
                            output(k(u(-a)),2)."""
            ),
            [
                Candidate(
                    pos=[],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        ),
                    ],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        )
                    ],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        )
                    ],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        ),
                    ],
                    neg=[],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        )
                    ],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        )
                    ],
                ),
            ],
        )

    def test_generator02_reification(self):

        # echo "-a. b :- &k{-a}. c :- &k{b}." | eclingo --semantics c19-1 --reification --output=reify
        self.assert_models(
            generate(
                """tag(incremental).
                                    atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)).
                                    atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)).
                                    atom_tuple(2). atom_tuple(2,3). literal_tuple(1).
                                    literal_tuple(1,2). rule(disjunction(2),normal(1)). atom_tuple(3).
                                    atom_tuple(3,4). literal_tuple(2). literal_tuple(2,3). rule(choice(3),normal(2)).
                                    atom_tuple(4). atom_tuple(4,5). literal_tuple(3). literal_tuple(3,4).
                                    rule(disjunction(4),normal(3)). output(k(u(-a)),1). output(k(u(b)),3). output(u(-a),0).
                                    output(u(b),2). literal_tuple(4). literal_tuple(4,5). output(u(c),4).
                                    rule(choice(1),normal(0)). rule(disjunction(2),normal(1)). rule(choice(3),normal(2)).
                                    rule(disjunction(4),normal(3))."""
            ),
            [
                # Candidate(pos=[], neg=[Function('k', [Function('u', [Function('b', [], True)], True)], True),
                #                           Function('k', [Function('u', [Function('a', [], False)], True)], True)]),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        ),
                    ],
                    neg=[],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        )
                    ],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        )
                    ],
                ),
            ],
        )

        # echo "{-a}. b :- &k{-a}. c :- &k{b}." | eclingo --semantics c19-1 --reification --output=reify
        self.assert_models(
            generate(
                """tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(choice(0),normal(0)).
                                    atom_tuple(1). atom_tuple(1,2). literal_tuple(1). literal_tuple(1,1). rule(choice(1),normal(1)).
                                    atom_tuple(2). atom_tuple(2,3). literal_tuple(2). literal_tuple(2,2). rule(disjunction(2),normal(2)).
                                    atom_tuple(3). atom_tuple(3,4). literal_tuple(3). literal_tuple(3,3). rule(choice(3),normal(3)).
                                    atom_tuple(4). atom_tuple(4,5). literal_tuple(4). literal_tuple(4,4). rule(disjunction(4),normal(4)).
                                    output(u(-a),1). output(u(b),3). literal_tuple(5). literal_tuple(5,5). output(u(c),5).
                                    output(k(u(-a)),2). output(k(u(b)),4)."""
            ),
            [
                Candidate(
                    pos=[],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        ),
                    ],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        ),
                    ],
                    neg=[],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], False)], True)], True
                        )
                    ],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        )
                    ],
                ),
            ],
        )

    def test_generator03_reification(self):
        # echo "{a}. :- not a. b :- &k{a}. c :- &k{b}." | eclingo --semantics c19-1 --reification --output=reify
        self.assert_models(
            generate(
                """tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                         rule(choice(0),normal(0)). atom_tuple(1). atom_tuple(1,2). literal_tuple(1).
                                         literal_tuple(1,1). rule(choice(1),normal(1)). atom_tuple(2). atom_tuple(2,3).
                                         literal_tuple(2). literal_tuple(2,2). rule(disjunction(2),normal(2)). atom_tuple(3).
                                         atom_tuple(3,4). literal_tuple(3). literal_tuple(3,3). rule(choice(3),normal(3)).
                                         atom_tuple(4). atom_tuple(4,5). literal_tuple(4). literal_tuple(4,4).
                                         rule(disjunction(4),normal(4)). atom_tuple(5). literal_tuple(5). literal_tuple(5,-1).
                                         rule(disjunction(5),normal(5)). output(u(a),1). output(u(b),3). literal_tuple(6).
                                         literal_tuple(6,5). output(u(c),6). output(k(u(a)),2). output(k(u(b)),4).
                                         rule(choice(0),normal(0)). rule(choice(1),normal(1)). rule(disjunction(2),normal(2)).
                                         rule(choice(3),normal(3)). rule(disjunction(4),normal(4)). rule(disjunction(5),normal(5))."""
            ),
            [
                Candidate(
                    pos=[],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("a", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                    ],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], True)], True)], True
                        )
                    ],
                    neg=[
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        )
                    ],
                ),
                Candidate(
                    pos=[
                        Function(
                            "k", [Function("u", [Function("a", [], True)], True)], True
                        ),
                        Function(
                            "k", [Function("u", [Function("b", [], True)], True)], True
                        ),
                    ],
                    neg=[],
                ),
            ],
        )


# class TestEclingoGeneratorReificationWithApproximation(TestCase):

#     def
